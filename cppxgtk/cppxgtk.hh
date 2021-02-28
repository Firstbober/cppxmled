#pragma once
#include "../cppxlib/cppxlib.hh"
#include <functional>
#include <gtk/gtk.h>
#include <gtkmm.h>
#include <string>

GtkApplication *__app;

static void __gtk_activate(GtkApplication *app, gpointer user_data) {
  cppx::Node *node = (cppx::Node *)user_data;
  node->init();
}

auto __renderCPPX(cppx::Node *node, int argc, char **argv) {
  __app = gtk_application_new("org.gtk.example", G_APPLICATION_FLAGS_NONE);
  g_signal_connect(__app, "activate", G_CALLBACK(__gtk_activate), node);
  g_application_run(G_APPLICATION(__app), argc, argv);
  g_object_unref(__app);
}

#define renderCPPX(root) __renderCPPX(root, argc, argv);

struct WindowGtkWrapper : public cppx::Node {
  GtkWindow *window;
  std::string title;
  cppx_props children;
  int width, height;

  WindowGtkWrapper(std::string title, cppx_props children, int width,
                   int height) {
    this->title = title;
    this->children = children;
    this->width = width;
    this->height = height;
  }
  ~WindowGtkWrapper() {}

  virtual auto init() -> void {
    window = GTK_WINDOW(gtk_application_window_new(__app));
    gtk_window_set_title(window, title.c_str());
    gtk_window_set_default_size(window, this->width, this->height);

    for (auto &&child : children) {
      child->init();
      if (GTK_IS_WIDGET(child->render())) {
        gtk_container_add(GTK_CONTAINER(window), GTK_WIDGET(child->render()));
      }
    }

    gtk_widget_show_all(GTK_WIDGET(window));
  }
  virtual auto render() -> void * { return nullptr; }
};

auto Window(cppx_props children, std::string title = "CPPX GTK Window",
            int width = 200, int height = 200) -> cppx::Node * {
  auto window = new WindowGtkWrapper(title, children, width, height);

  return window;
}

struct TextGtkWrapper : public cppx::Node {
  std::string text;
  GtkLabel *label;

  TextGtkWrapper(std::string text) { this->text = text; }
  ~TextGtkWrapper() {}

  virtual auto init() -> void {
    label = GTK_LABEL(gtk_label_new(this->text.c_str()));
  }
  virtual auto render() -> void * { return GTK_WIDGET(label); }
};
auto Text(cppx_props children, std::string text) -> cppx::Node * {
  return new TextGtkWrapper(text);
}

struct BoxGtkWrapper : public cppx::Node {
  GtkBox *box;
  cppx_props children;
  std::string orientation;

  BoxGtkWrapper(cppx_props children, std::string orientation) {
    this->children = children;
    this->orientation = orientation;
  }
  ~BoxGtkWrapper() {}

  virtual auto init() -> void {
    if (this->orientation == "vertical") {
      box = GTK_BOX(gtk_box_new(GTK_ORIENTATION_VERTICAL, 0));
    } else if (this->orientation == "horizontal") {
      box = GTK_BOX(gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0));
    }

    for (auto &&child : children) {
      child->init();
      if (GTK_IS_WIDGET(child->render())) {
        gtk_box_pack_start(box, GTK_WIDGET(child->render()), true, true, 0);
      }
    }

    gtk_widget_show_all(GTK_WIDGET(box));
  }
  virtual auto render() -> void * { return GTK_WIDGET(box); }
};

auto View(cppx_props children, std::string orientation = "vertical")
    -> cppx::Node * {
  return new BoxGtkWrapper(children, orientation);
}

struct ButtonGtkWrapper : public cppx::Node {
  Gtk::Button *button;
  std::string label;
  std::function<void()> onClick;
  cppx_props children;

  ButtonGtkWrapper(cppx_props children, std::string label,
                   std::function<void()> onClick) {
    this->children = children;
    this->label = label;
    this->onClick = onClick;
  }
  ~ButtonGtkWrapper() {}

  virtual auto init() -> void {
    Glib::init();
    this->button = new Gtk::Button(this->label);
    this->button->signal_pressed().connect(onClick);
  }
  virtual auto render() -> void * { return GTK_WIDGET(button->gobj()); }
};

auto Button(cppx_props children, std::string label,
            std::function<void()> onClick = {}) -> cppx::Node * {
  return new ButtonGtkWrapper(children, label, onClick);
}