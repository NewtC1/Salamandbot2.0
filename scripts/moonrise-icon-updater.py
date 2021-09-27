import obspython as obs
import json

interval = 5
status_directory = ""


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

    with open(status_directory, encoding="utf-8-sig", mode="r") as file_reader:
        status = json.load(file_reader)

    try:
        set_source_visibility("Soil Ready", status["soil_ready"])
        set_source_visibility("Soil Kill", status["soil_kill"])
        set_source_visibility("Bjorn Ready", status["bjorn_ready"])
        set_source_visibility("Bjorn Splinter", status["bjorn_delay"])
    except Exception as err:
        obs.script_log(obs.LOG_WARNING, err)


def refresh_pressed(props, prop):
    update_icons()


# ------------------------------------------------------------

def script_description():
    return "Updates icons required for the Moonrise stream event.\n\nBy NewtC"


def script_update(settings):
    global interval
    global status_directory

    interval = obs.obs_data_get_int(settings, "interval")
    status_directory = obs.obs_data_get_string(settings, "status_directory")
    obs.timer_remove(update_icons)

    if status_directory and interval:
        obs.timer_add(update_icons, interval * 1000)


def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "interval", 30)
    obs.obs_data_set_string(settings, "status_directory", "..\\values\\moonrise_status.json")


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "status_directory", "Status Directory", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 5, 3600, 1)

    obs.obs_properties_add_button(props, "button", "Refresh:", refresh_pressed)
    return props
