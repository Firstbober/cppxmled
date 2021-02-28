#include <iostream>
#include "../../cppxlib/cppxlib.hh"
#include "../../cppxgtk/cppxgtk.hh"

auto WelcomeTexts() -> auto {
	return cppx(
		<View>
			<Text>Hello and, again,</Text>
			<Text>welcome to the Aperture Science</Text>
			<Text>computer-aided enrichment center.</Text>
		</View>
	);
}

auto onClick_secondButton() -> void {
	std::cout << "Clicked second button!\n";
}

auto RandomButtons() -> auto {
	auto clickedFirst = []() {
		std::cout << "Clicked first button!\n";
	};

	auto clickedLast = []() {
		std::cout << "Clicked last button!\n";
	};

	return cppx(
		<View>
			<Button onClick={clickedFirst}>First</Button>

			<Button onClick={onClick_secondButton}>Last</Button>

			<Button onClick={clickedLast}>Second</Button>
		</View>
	);
}

auto App() -> auto {
	return cppx(
		<Window title="Example: Meson + CPPX + GTK3" width="600">
			<View orientation="horizontal">
				{WelcomeTexts()}
				{RandomButtons()}
			</View>
		</Window>
	);
}

cppx_main {
	renderCPPX(App());
	return 0;
}