import obspython as obs
import json
import os

interval = 5
status_directory = ""
started = False


# ------------------------------------------------------------

def set_source_visibility(source_name: str, visibilty: bool):
    global interval

    source = obs.obs_get_source_by_name(source_name)
    obs.script_log(obs.LOG_INFO, f"Changing source visibility of {source_name} to {visibilty}")

    if source:
        current_scene = obs.obs_scene_from_source(obs.obs_frontend_get_current_scene())
        scene_item = obs.obs_scene_find_source(current_scene, source_name)
        obs.obs_sceneitem_set_visible(scene_item, visibilty)


def update_icons():
    global status_directory
    obs.timer_remove(update_icons)
    with open(status_directory, encoding="utf-8-sig", mode="r") as file_reader:
        status = json.load(file_reader)

    try:
        set_source_visibility("Soil Ready", status["soil_ready"])
        set_source_visibility("Soil Kill", status["soil_kill"])
        set_source_visibility("Bjorn Ready", status["bjorn_ready"])
        set_source_visibility("Bjorn Splinter", status["bjorn_delay"])
        obs.timer_add(update_icons, interval * 1000)
    except Exception as err:
        obs.script_log(obs.LOG_WARNING, err)


def refresh_pressed(props, prop):
    update_icons()


def start_pressed(props, prop):
    global started
    started = not started
    obs.script_log(obs.LOG_INFO, f"Settings started to: {started}")

    if started:
        obs.timer_add(update_icons, interval * 1000)
    else:
        obs.timer_remove(update_icons)


# ------------------------------------------------------------

def script_description():
    return "Updates icons required for the Moonrise stream event.\n\nBy NewtC"


def script_defaults(settings):
    global status_directory
    obs.obs_data_set_default_int(settings, "interval", 30)
    path_to_script_dir = "\\".join(os.path.realpath(__file__).split("\\")[0:-1])
    default_dir = os.path.join(path_to_script_dir, "..\\values\\moonrise_status.json")
    status_directory = default_dir
    obs.script_log(obs.LOG_INFO, f"Current working directory: {default_dir}")
    obs.obs_data_set_string(settings, "status_directory", default_dir)


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "status_directory", "Status Directory", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 5, 3600, 1)

    obs.obs_properties_add_button(props, "button", "Start\\Stop", start_pressed)
    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props
