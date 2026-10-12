from ._anvil_designer import RowTemplateTemplate
from anvil import *


class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
