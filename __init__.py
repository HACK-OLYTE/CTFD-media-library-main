from flask import Blueprint, render_template, request, jsonify
from CTFd.plugins import register_admin_plugin_menu_bar, register_plugin_assets_directory
from CTFd.utils import get_config, set_config
from CTFd.utils.decorators import admins_only
from CTFd.utils.user import is_admin


def load(app):
    blueprint = Blueprint(
        "ctfd_media_library",
        __name__,
        template_folder="templates",
        url_prefix="/plugins/media-library",
    )

    @blueprint.route("/")
    @admins_only
    def media_page():
        show_icon = bool(get_config("media_library_show_icon"))
        return render_template("index.html", show_icon=show_icon)

    @blueprint.route("/toggle-icon", methods=["POST"])
    @admins_only
    def toggle_icon():
        data = request.get_json(silent=True) or {}
        enabled = bool(data.get("enabled", False))
        set_config("media_library_show_icon", enabled)
        return jsonify({"success": True, "enabled": enabled})

    @app.after_request
    def inject_media_widget(response):
        if response.content_type.startswith("text/html"):
            if request.path.startswith("/admin") and is_admin():
                if get_config("media_library_show_icon"):
                    html = response.get_data(as_text=True)
                    if "</body>" in html:
                        widget = render_template("widget.html")
                        response.set_data(html.replace("</body>", widget + "</body>", 1))
        return response

    app.register_blueprint(blueprint)
    register_plugin_assets_directory(app, base_path="/plugins/ctfd-media-library-main/assets/")

    register_admin_plugin_menu_bar(
        title="Media",
        route="/plugins/media-library/",
    )
