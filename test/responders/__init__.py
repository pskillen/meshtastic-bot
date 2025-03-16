from abc import ABC

from src.responders.responder import AbstractResponder
from test import BaseFeatureTestCase


class ResponderTestCase(BaseFeatureTestCase, ABC):
    responder: AbstractResponder
