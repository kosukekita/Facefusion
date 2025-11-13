import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import gradio

from facefusion import state_manager, translator
from facefusion.uis.core import register_ui_component

FOLDER_DROPDOWN : Optional[gradio.Dropdown] = None
OUTPUT_PATH_TEXTBOX : Optional[gradio.Textbox] = None
OUTPUT_IMAGE : Optional[gradio.Image] = None
OUTPUT_VIDEO : Optional[gradio.Video] = None


def render() -> None:
	global FOLDER_DROPDOWN
	global OUTPUT_PATH_TEXTBOX
	global OUTPUT_IMAGE
	global OUTPUT_VIDEO

	if not state_manager.get_item('output_path'):
		default_output_directory = Path('/home/kita/pCloudDrive/Code/Applications/Facefusion/Output')
		if default_output_directory.exists():
			state_manager.set_item('output_path', str(default_output_directory))
		else:
			state_manager.set_item('output_path', tempfile.gettempdir())

	folder_choices = create_folder_choices()
	selected_output_path = state_manager.get_item('output_path')

	# 一覧に現在の出力パスが含まれていない場合は追加する
	if selected_output_path and selected_output_path not in [ value for _, value in folder_choices ]:
		folder_choices.insert(0, (format_label(Path(selected_output_path)), selected_output_path))

	FOLDER_DROPDOWN = gradio.Dropdown(
		label = translator.get('uis.output_path_textbox') + ' (検索可能)',
		choices = folder_choices,
		value = selected_output_path,
		allow_custom_value = True,
		filterable = True
	)
	OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = '選択された出力パス',
		value = selected_output_path,
		max_lines = 1,
		interactive = False
	)
	OUTPUT_IMAGE = gradio.Image(
		label = translator.get('uis.output_image_or_video'),
		visible = False
	)
	OUTPUT_VIDEO = gradio.Video(
		label = translator.get('uis.output_image_or_video')
	)


def listen() -> None:
	FOLDER_DROPDOWN.change(update_output_path, inputs = FOLDER_DROPDOWN, outputs = OUTPUT_PATH_TEXTBOX)
	register_ui_component('output_image', OUTPUT_IMAGE)
	register_ui_component('output_video', OUTPUT_VIDEO)


def create_folder_choices() -> List[Tuple[str, str]]:
	"""pCloud Drive内のディレクトリを、階層を保った状態で一覧化"""
	base_path = Path('/home/kita/pCloudDrive')
	folder_map : Dict[str, str] = {}

	try:
		for root, dirs, _ in os.walk(base_path):
			root_path = Path(root)
			# 深さを制限（0: pCloudDrive, 1: 第一階層, 2: 第二階層, 3: 第三階層）
			depth = len(root_path.relative_to(base_path).parts) if root_path != base_path else 0
			if depth > 3:
				dirs[:] = []
				continue

			# 隠しフォルダを除外
			dirs[:] = [ directory for directory in dirs if not directory.startswith('.') ]
			folder_map[str(root_path)] = format_label(root_path)

	except Exception:
		pass

	# 表示ラベルでソート（pCloudDrive自体を先頭に）
	sorted_items = sorted(folder_map.items(), key = lambda item: item[0])
	choices = [ (label, path) for path, label in sorted_items ]
	return choices[:150]


def format_label(path : Path) -> str:
	base_path = Path('/home/kita/pCloudDrive')
	if path == base_path:
		return 'pCloudDrive'
	try:
		relative_parts = path.relative_to(base_path).parts
		return ' / '.join(relative_parts)
	except ValueError:
		return str(path)


def update_output_path(selected_path : str) -> str:
	if selected_path:
		state_manager.set_item('output_path', selected_path)
		return selected_path
	return state_manager.get_item('output_path')
