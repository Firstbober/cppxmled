# cppxmled
Simple preprocessor for c++ which adds support for inline XML with native c++ code gen.
Made just for fun.

Example:

```cpp
#include <iostream>
#include "../../cppxlib/cppxlib.hh"
#include "../../cppxgtk/cppxgtk.hh"

auto App() -> auto {
	return cppx(
		<Window title="Example: Meson + CPPX + GTK3">
			<Text>Hello, world!</Text>
		</Window>
	);
}

cppx_main {
	renderCPPX(App());
	return 0;
}
```

More in `example-meson-cppx-gtk`

## Memleaks are everywhere and there is no support for states!

# cppxgtk docs
**Order of attributes is important!!**

## <Window> - creates GTK window
### title="Some title"
### width="300"
### height="300"

## <View> - container for elements (based on GtkBox)
### orientation="vertical/horizontal"
**Default orientation is vertical**

## <Text> - text
### <Text>some text</Text>

## <Button> - button
### onClick={onButtonClick}
### <Button ...>Some button label</Button>