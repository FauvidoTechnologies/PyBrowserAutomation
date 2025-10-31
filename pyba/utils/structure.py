from dataclasses import dataclass, field
from typing import Optional, List

from pydantic import BaseModel


class PlaywrightAction(BaseModel):
    """
    The BaseModel for playwright automations

    Goal:
        This contains an exhaustive list of commands that playwright can execute. It
        will be filled accordingly by the LLM depending on the DOM recieved from playwright
        and the goal of the task.
    """

    goto: Optional[str]
    go_back: Optional[bool]
    go_forward: Optional[bool]
    reload: Optional[bool]

    click: Optional[str]
    dblclick: Optional[str]
    hover: Optional[str]
    fill_selector: Optional[str]
    fill_value: Optional[str]
    type_selector: Optional[str]
    type_text: Optional[str]
    press_selector: Optional[str]
    press_key: Optional[str]
    check: Optional[str]
    uncheck: Optional[str]
    select_selector: Optional[str]
    select_value: Optional[str]
    upload_selector: Optional[str]
    upload_path: Optional[str]

    scroll_x: Optional[int]
    scroll_y: Optional[int]
    wait_selector: Optional[str]
    wait_timeout: Optional[int]
    wait_ms: Optional[int]

    keyboard_press: Optional[str]
    keyboard_type: Optional[str]
    mouse_move_x: Optional[int]
    mouse_move_y: Optional[int]
    mouse_click_x: Optional[int]
    mouse_click_y: Optional[int]

    new_page: Optional[str]
    close_page: Optional[bool]
    switch_page_index: Optional[int]

    evaluate_js: Optional[str]
    screenshot_path: Optional[str]
    download_selector: Optional[str]


class PlaywrightResponse(BaseModel):
    actions: List[PlaywrightAction]


class OutputResponseFormat(BaseModel):
    """
    Output type for the model for direct response
    """

    output: str


@dataclass
class CleanedDOM:
    """
    Represents the cleaned DOM snapshot of the current browser page.

    Additional parameter for the youtube DOM extraction
    """

    hyperlinks: Optional[List[str]] = field(default_factory=list)
    input_fields: Optional[List[str]] = field(default_factory=list)
    clickable_fields: Optional[List[str]] = field(default_factory=list)
    actual_text: Optional[str] = None
    current_url: Optional[str] = None
    youtube: Optional[str] = None  # For YouTube based DOM extraction

    def to_dict(self) -> dict:
        return {
            "hyperlinks": self.hyperlinks,
            "input_fields": self.input_fields,
            "clickable_fields": self.clickable_fields,
            "actual_text": self.actual_text,
            "current_url": self.current_url,
            "youtube": self.youtube,
        }
