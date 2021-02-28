#pragma once

#include <iostream>
#include <string>
#include <vector>

namespace cppx {

struct Node {
	Node() {}
	virtual ~Node() {}

	virtual auto init() -> void = 0;
	virtual auto render() -> void * = 0;
};

struct DummyNode :public Node {
	DummyNode() {}
	~DummyNode() {}

	virtual auto init() -> void {};
	virtual void *render() { return nullptr; };
};

}

#define cppx_main auto main(int argc, char **argv) -> int

#define cppx(...) new cppx::DummyNode;
#define cppx_props std::vector<cppx::Node *>
#define cppxReturn new cppx::DummyNode;
#define cppx_inline_fn [=]()