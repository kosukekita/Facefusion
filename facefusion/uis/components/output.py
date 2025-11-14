import tempfile
from pathlib import Path
from typing import Optional

import gradio

from facefusion import state_manager, translator
from facefusion.uis.core import register_ui_component

OUTPUT_PATH_TEXTBOX : Optional[gradio.Textbox] = None
OUTPUT_IMAGE : Optional[gradio.Image] = None
OUTPUT_VIDEO : Optional[gradio.Video] = None


def resolve_default_output_directory() -> Path:
	repository_root = Path(__file__).resolve().parents[3]
	default_directory = repository_root / 'Output'

	if default_directory.exists():
		return default_directory

	return Path(tempfile.gettempdir())


def render() -> None:
	global OUTPUT_PATH_TEXTBOX
	global OUTPUT_IMAGE
	global OUTPUT_VIDEO

	if not state_manager.get_item('output_path'):
		state_manager.set_item('output_path', str(resolve_default_output_directory()))

	OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = translator.get('uis.output_path_textbox'),
		value = state_manager.get_item('output_path'),
		max_lines = 1,
		placeholder = str(resolve_default_output_directory()),
		interactive = True
	)
	OUTPUT_IMAGE = gradio.Image(
		label = translator.get('uis.output_image_or_video'),
		visible = False
	)
	OUTPUT_VIDEO = gradio.Video(
		label = translator.get('uis.output_image_or_video')
	)


def listen() -> None:
	OUTPUT_PATH_TEXTBOX.change(update_output_path_from_textbox, inputs = OUTPUT_PATH_TEXTBOX, outputs = OUTPUT_PATH_TEXTBOX)
	register_ui_component('output_image', OUTPUT_IMAGE)
	register_ui_component('output_video', OUTPUT_VIDEO)


def update_output_path_from_textbox(output_path : str) -> str:
	if output_path:
		normalized_path = str(Path(output_path).expanduser())
		state_manager.set_item('output_path', normalized_path)
		return normalized_path

	state_manager.clear_item('output_path')
	default_path = str(resolve_default_output_directory())
	state_manager.set_item('output_path', default_path)
	return default_path
