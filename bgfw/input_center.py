from enum import Enum, auto
import re

class InputResult(Enum):
	
	COMMAND_EXECUTED = auto()
	COMMAND_FAILED = auto()
	COMMAND_NOT_RECOGNIZED = auto()

class Input_Center:

	def __init__(self, input_func=None):

		self.__registered_events = {}
		self.__unknown_command_response = (self.__default_unknown_command_response, (), {})
		self.__input_func = input if input_func == None else input_func

	def __default_unknown_command_response(self, *argv):

		print("Input not recognized")

	def __get_registered_events(self):

		return self.__registered_events

	def __get_event(self, label):

		return self.__registered_events[label]

	def __get_unknown_event(self):

		return self.__unknown_command_response

	def __matches_label(self, label, command):

		if label not in self.__get_registered_events():
			raise KeyError("label {} is not a registered label".format(label))

		trigger_func, _, args, kwargs = self.__get_event(label)
		return trigger_func(command, args, kwargs)

	def __execute_inputted_command(self, labels, command, inputer=None):

		for label in labels:
			if self.__matches_label(label, command):
				_, func, args, kwargs = self.__get_event(label)
				execution_result, success = func(command, inputer, args, kwargs)
				if success:
					return InputResult.COMMAND_EXECUTED, execution_result 
				else:
					return InputResult.COMMAND_FAILED, execution_result

		func, args, kwargs = self.__get_unknown_event()
		execution_result = func(command, args)
		return InputResult.COMMAND_NOT_RECOGNIZED, execution_result

	def add_input_response(self, label, trigger_func, func, *args, **kwargs):

		""" maps a regular expression to a function to be executed when that condition is met -- label identifies the triplet"""

		self.__registered_events[label] = (trigger_func, func, args, kwargs)

	def add_unknown_input_response(self, func, *args, **kwargs):

		""" registers the function to be called when an inputted command is not recognized """

		self.__unknown_command_response = (func, None, args, kwargs)


	def listen(self, labels, end_label="", max_commands=float("inf"), inputer=None, participants_to_poll=None):

		""" listens for the specified inputs and executes their associated commands """

		for label in labels:
			if label not in self.__get_registered_events():
				raise KeyError("label {} is not a registered label".format(label))

		command_count = 0
		command = self.__input_func()

		while (re.search(end_label, command) == None or end_label == "") and command_count < max_commands:
			success, result = self.__execute_inputted_command(labels, command, inputer)
			if success == InputResult.COMMAND_EXECUTED:
				command_count += 1
			if command_count < max_commands:
				command = self.__input_func()

		print()

