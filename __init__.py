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

        normalize_images = get_config("media_library_normalize_images")
        if normalize_images is None:
            normalize_images = True
        else:
            normalize_images = bool(normalize_images)

        optimize_uploads = get_config("media_library_optimize_uploads")
        if optimize_uploads is None:
            optimize_uploads = True
        else:
            optimize_uploads = bool(optimize_uploads)

        return render_template(
            "index.html",
            show_icon=show_icon,
            normalize_images=normalize_images,
            optimize_uploads=optimize_uploads,
        )

    @blueprint.route("/toggle-icon", methods=["POST"])
    @admins_only
    def toggle_icon():
        data = request.get_json(silent=True) or {}
        enabled = bool(data.get("enabled", False))
        set_config("media_library_show_icon", enabled)
        return jsonify({"success": True, "enabled": enabled})

    @blueprint.route("/toggle-normalize-images", methods=["POST"])
    @admins_only
    def toggle_normalize_images():
        data = request.get_json(silent=True) or {}
        enabled = bool(data.get("enabled", True))
        set_config("media_library_normalize_images", enabled)
        return jsonify({"success": True, "enabled": enabled})

    @blueprint.route("/toggle-optimize-uploads", methods=["POST"])
    @admins_only
    def toggle_optimize_uploads():
        data = request.get_json(silent=True) or {}
        enabled = bool(data.get("enabled", True))
        set_config("media_library_optimize_uploads", enabled)
        return jsonify({"success": True, "enabled": enabled})

    @app.after_request
    def inject_media_widget(response):
        if response.content_type.startswith("text/html"):
            if request.path.startswith("/admin") and is_admin():
                if get_config("media_library_show_icon"):
                    html = response.get_data(as_text=True)
                    if "</body>" in html:
                        widget = render_template("widget.html")
                        response.set_data(
                            html.replace("</body>", widget + "</body>", 1)
                        )
        return response

    app.register_blueprint(blueprint)

    # Fix case-sensitive asset path on Linux
    register_plugin_assets_directory(
        app,
        base_path="/plugins/CTFD-media-library-main/assets/",
    )

    register_admin_plugin_menu_bar(
        title="Media",
        route="/plugins/media-library/",
    )
