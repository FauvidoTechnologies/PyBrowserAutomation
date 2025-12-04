from dataclasses import dataclass, field
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class PlaywrightAction(BaseModel):
    """
    The BaseModel for playwright automations

    Goal:
        This contains an exhaustive list of commands that playwright can execute. It
        will be filled accordingly by the LLM depending on the DOM recieved from playwright
        and the goal of the task.
    """

    # Navigation
    goto: Optional[str] = Field(None, description="Navigate to the given URL using page.goto().")
    go_back: Optional[bool] = Field(
        None, description="Navigate back in browser history using page.go_back()."
    )
    go_forward: Optional[bool] = Field(
        None, description="Navigate forward in browser history using page.go_forward()."
    )
    reload: Optional[bool] = Field(
        None, description="Reload the current page using page.reload()."
    )

    # Interaction
    click: Optional[str] = Field(
        None, description="Click the specified element using page.click(selector)."
    )
    dblclick: Optional[str] = Field(
        None, description="Double-click the specified element using page.dblclick(selector)."
    )
    hover: Optional[str] = Field(
        None, description="Hover over the specified element using page.hover(selector)."
    )
    right_click: Optional[str] = Field(
        None,
        description="Right click a specified element using page.click(selector, button='right')",
    )

    # Dropdowns
    dropdown_field_id: Optional[str] = Field(
        None, description="Select the ID of the dropdown field"
    )
    dropdown_field_value: Optional[str] = Field(
        None, description="The value to be selected from the dropdown field"
    )
    # Input
    fill_selector: Optional[str] = Field(
        None, description="Selector of the input element to fill using page.fill()."
    )
    fill_value: Optional[str] = Field(
        None, description="Value to fill into the element specified by fill_selector."
    )
    type_selector: Optional[str] = Field(
        None, description="Selector of the input element to type into using page.type()."
    )
    type_text: Optional[str] = Field(
        None, description="Text to type into the element specified by type_selector."
    )
    press_selector: Optional[str] = Field(
        None,
        description="Selector of the element to send a key press event to using page.press().",
    )
    press_key: Optional[str] = Field(
        None, description="Key to press (e.g., 'Enter', 'Escape', 'ArrowDown') in page.press()."
    )
    check: Optional[str] = Field(
        None, description="Selector of a checkbox or radio button to check using page.check()."
    )
    uncheck: Optional[str] = Field(
        None, description="Selector of a checkbox or radio button to uncheck using page.uncheck()."
    )
    select_selector: Optional[str] = Field(
        None, description="Selector of a <select> element to modify using page.select_option()."
    )
    select_value: Optional[str] = Field(
        None, description="Option value to select within the element specified by select_selector."
    )
    upload_selector: Optional[str] = Field(
        None,
        description="Selector of a file input element to upload a file using page.set_input_files().",
    )
    upload_path: Optional[str] = Field(
        None, description="Path to the file(s) to upload for upload_selector."
    )

    # Scrolling and Waiting
    scroll_x: Optional[int] = Field(
        None, description="Horizontal scroll position to move to using page.evaluate()."
    )
    scroll_y: Optional[int] = Field(
        None, description="Vertical scroll position to move to using page.evaluate()."
    )
    wait_selector: Optional[str] = Field(
        None, description="Selector to wait for before proceeding using page.wait_for_selector()."
    )
    wait_timeout: Optional[int] = Field(
        None, description="Maximum time (in ms) to wait for the selector or event."
    )
    wait_ms: Optional[int] = Field(
        None, description="Wait for a fixed duration (in milliseconds) using time.sleep()."
    )

    # Keyboard and Mouse
    keyboard_press: Optional[str] = Field(
        None, description="Key to simulate a keyboard press event using page.keyboard.press()."
    )
    keyboard_type: Optional[str] = Field(
        None, description="Text to type using page.keyboard.type()."
    )
    mouse_move_x: Optional[int] = Field(
        None, description="X-coordinate to move the mouse to using page.mouse.move()."
    )
    mouse_move_y: Optional[int] = Field(
        None, description="Y-coordinate to move the mouse to using page.mouse.move()."
    )
    mouse_click_x: Optional[int] = Field(
        None, description="X-coordinate for a direct mouse click using page.mouse.click()."
    )
    mouse_click_y: Optional[int] = Field(
        None, description="Y-coordinate for a direct mouse click using page.mouse.click()."
    )

    # Page and Context Management
    new_page: Optional[str] = Field(
        None, description="Create a new browser page (optionally with a given URL)."
    )
    close_page: Optional[bool] = Field(
        None, description="Close the current page using page.close()."
    )
    switch_page_index: Optional[int] = Field(
        None, description="Switch to another open page by its index in context.pages()."
    )

    # Evaluation and Utilities
    evaluate_js: Optional[str] = Field(
        None, description="Run JavaScript code in the browser context using page.evaluate()."
    )
    screenshot_path: Optional[str] = Field(
        None, description="Path to save a screenshot using page.screenshot()."
    )
    download_selector: Optional[str] = Field(
        None, description="Selector to trigger a download event from (e.g., a link or button)."
    )


class PlaywrightResponse(BaseModel):
    actions: List[PlaywrightAction]
    extract_info: Optional[bool] = Field(
        ...,
        description="A specific boolean value for the playwright agent to decide if extraction is required from this page",
    )


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


class PlannerAgentOutputBFS(BaseModel):
    """
    BFS planner agent output
    """

    plans: List[str] = Field(
        ..., description="List of potential plans that can should be executed in parallel"
    )


class PlannerAgentOutputDFS(BaseModel):
    """
    DFS planner agent output
    """

    plan: str = Field(
        ..., description="A single plan to be executed in depth to achieve the required goal"
    )


class GeneralExtractionResponse(BaseModel):
    """
    The general extraction agent output. This is used when the user hasn't specified an
    output format themselves
    """

    imp_visible_text: str = Field(
        ...,
        description="A bunch of visible text on the current page which matches what the user is asking for",
    )
    general_dict: Optional[Dict[str, str]] = Field(
        ...,
        description="An optional dictionay in case the user's output requirement suits this better",
    )
