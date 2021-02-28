project('example-meson-cppx_gtk', 'cpp',
	version: '1.0.0',
	default_options: [
		'cpp_std=c++17',
		'build.cpp_std=c++17'
	])

deps = [
	dependency('gtk+-3.0'),
	dependency('gtkmm-3.0')
]

sources = [
	'src/main.cc'
]

prog_python = import('python').find_installation('python3')
cppx_gen = generator(prog_python,
                output  : '@BASENAME@.cc',
                arguments : [meson.source_root() + '/../cppxc/cppxc.py', '@INPUT@', '@OUTPUT@'])

generated_sources = cppx_gen.process(sources)

executable(
	'simple-cppx-gtk',
	generated_sources,
	dependencies: deps,
	install: true,
)