import argparse
import re
import xml.etree.ElementTree as ET
import os

parser = argparse.ArgumentParser(description="Compile cppx to cpp code")
parser.add_argument("file", type=str, nargs="+", help="File to compile")
parser.add_argument("output", type=str, nargs="+", help="File to put code in")

args = parser.parse_args()
FILE_TO_COMPILE = args.file[0]
f = open(FILE_TO_COMPILE, "r")

file_content = f.read()

CURR_ID = 0

def getUniqueId():
    global CURR_ID
    to_ret = CURR_ID
    CURR_ID += 1
    return to_ret

def gen_CPPX_INTERNAL_INLINECPP(code):
    return "<__cppx_internal_InlineCPP><![CDATA[" + code + "]]></__cppx_internal_InlineCPP>"

def get_all_cppx_references(code_string):
    references = []

    for apperance in re.finditer("cppx", code_string):
        isCppX = False
        cppXCheckFailed = False
        foundOffset = False
        exitLoop = False

        parenthesisOpenCount = 0
        parenthesisClosedCount = 0
        cppXContentOffset = 4

        cppXContent = ""

        for character in code_string[apperance.span()[1] :]:
            if cppXCheckFailed or exitLoop:
                continue

            if not foundOffset:
                cppXContentOffset += 1

            if (
                not (
                    character == "\n"
                    or character == " "
                    or character == "\t"
                    or character == "\r"
                )
                and isCppX == False
            ):
                if character == "(":
                    isCppX = True
                    parenthesisOpenCount += 1
                    foundOffset = True
                    continue
                else:
                    cppXCheckFailed = True

            if isCppX:
                if parenthesisOpenCount == parenthesisClosedCount:
                    isCppX = False
                    exitLoop = True
                    cppXContent = cppXContent[:-1]
                    continue

                if character == "(":
                    parenthesisOpenCount += 1
                if character == ")":
                    parenthesisClosedCount += 1

                cppXContent += character

        if cppXCheckFailed == False:
            references.append(
                [
                    cppXContent.strip(),
                    code_string[apperance.span()[0] :][
                        : len(cppXContent) + cppXContentOffset
                    ]
                    + ")",
                ]
            )

    return references

def convert_cpp_references_to_xml(xml_code):
    curlyBracketOpenCount = 0
    curlyBracketClosedCount = 0

    canBeCppReferenceQuote = False
    arrowRightCount = 0
    arrowLeftCount = 0

    canBeCppReference = True
    canBeTagAttribute = False
    isTagAttibute = False

    cppReferenceContent = ""
    cppReferenceContents = []

    xml_code = xml_code.replace("\n", "")

    for character in xml_code:
        if character == ">":
            arrowRightCount += 1

        if character == "<":
            arrowLeftCount += 1

        if (character == '"' or character == "'") and arrowRightCount == arrowLeftCount:
            canBeCppReference = not canBeCppReference

        if isTagAttibute:
            canBeCppReference = True

        if canBeCppReference:
            if character == "=":
                canBeTagAttribute = True
                continue

            if (
                not (
                    character == "\n"
                    or character == " "
                    or character == "\t"
                    or character == "\r"
                )
                and isTagAttibute == False
                and canBeTagAttribute == True
            ):
                if character == "{":
                    curlyBracketOpenCount += 1
                    isTagAttibute = True
                else:
                    canBeTagAttribute = False

            if character == "{" and canBeTagAttribute == False:
                curlyBracketOpenCount += 1

            if character == "}":
                curlyBracketClosedCount += 1

            if curlyBracketOpenCount != curlyBracketClosedCount:
                cppReferenceContent += character
            else:
                if cppReferenceContent != "":
                    if cppReferenceContent.startswith("{cppx_inline_fn"):
                        cppReferenceContent += "}"

                    cppReferenceContents.append(
                        [cppReferenceContent[1:], cppReferenceContent + "}", isTagAttibute]
                    )
                isTagAttibute = False
                cppReferenceContent = ""
                arrowRightCount = 0
                arrowLeftCount = 0

    finalCompiledReferences = []

    for cppReference in cppReferenceContents:
        cppCode = ""
        xmlCode = ""

        if cppReference[0][-1:] == ";":
            cppReference[0] = cppReference[0][:-1]

        cppReference[0] = cppReference[0].replace("\t", "")

        callsFr = cppReference[0].split(";")
        clCounter = 0

        calls = []
        foundCurlyBracket = False

        for cla in callsFr:
            cle = cla.strip()

            if cle != "":
                if cle != "}":
                    calls.append(cla.strip())
                else:
                    foundCurlyBracket = True


        cppCode += "[=]() {"
        for cl in calls:
            if clCounter == len(calls)-1:
                cppCode += "return " + cl + ";"
                if foundCurlyBracket:
                    cppCode += "};"
            else:
                cppCode += cl + ";"

            clCounter += 1
        cppCode += "}()"

        if cppReference[2]:
            cppCode = cppCode.replace('"', '&quot;')
            cppCode = cppCode.replace("'", '&apos;')
            cppCode = cppCode.replace('&', '&amp;')
            cppCode = cppCode.replace('<', '&lt;')
            cppCode = cppCode.replace('>', '&gt;')

            xmlCode += "__cppx_param_inline_cpp__" + cppCode
        else:
            xmlCode += gen_CPPX_INTERNAL_INLINECPP(cppCode)
        finalCompiledReferences.append([xmlCode, cppReference[2], cppReference[1]])

    for finalRef in finalCompiledReferences:
        if finalRef[1]:
            xml_code = xml_code.replace(finalRef[2], "\"" + finalRef[0] + "\"")
        else:
            xml_code = xml_code.replace(finalRef[2], finalRef[0])

    return xml_code

def compile_xml_element(element):
    if element.tag == "__cppx_internal_InlineCPP":
        cpp_code = element.text
        return cpp_code

    cpp_code = element.tag + "({"
    elCount = 0
    attrCount = 0

    for el in element:
        cpp_code += compile_xml_element(el)
        cpp_code += ","
        elCount += 1

    if elCount > 0:
        cpp_code = cpp_code[:-1]

    cpp_code += "},"

    if element.text != "":
        element.text = element.text.strip()

        if element.text != "":
            element.text = element.text.replace("\t", "")
            if element.text[-1:] == "\"":
                element.text = element.text[:-1]
            if element.text[:1] == "\"":
                element.text = element.text[1:]

            if element.text.isnumeric():
                cpp_code += element.text + ","
            else:
                cpp_code += "\"" + element.text + "\","

    for attr in element.attrib.items():
        attcnt = attr[1]
        attcnt = attcnt.replace('&quot;', '"')
        attcnt = attcnt.replace('&apos;', "'")
        attcnt = attcnt.replace('&amp;', '&')
        attcnt = attcnt.replace('&lt;', '<')
        attcnt = attcnt.replace('&gt;', '>')

        if attcnt.startswith("__cppx_param_inline_cpp__"):
           cpp_code += attcnt[len("__cppx_param_inline_cpp__"):]
        else:
            if attcnt.isnumeric():
                cpp_code += attcnt
            else:
                cpp_code += "\"" + attcnt + "\""

        cpp_code += ","
        attrCount += 1

    if attrCount > 0:
        cpp_code = cpp_code[:-1]

    if cpp_code[-1:] == ",":
        cpp_code = cpp_code[:-1]

    cpp_code += ")"
    return cpp_code

references = get_all_cppx_references(file_content)

for ref in references:
    converted_xml_code = convert_cpp_references_to_xml(ref[0])
    cpp_code = compile_xml_element(ET.fromstring(converted_xml_code))

    file_content = file_content.replace(ref[1], cpp_code)

f = open(args.output[0], "w")
f.write(file_content)
f.close()