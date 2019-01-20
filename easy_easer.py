#!/usr/env python

import pytweening
import types

TweeningFunctions = [ i for i in
                        list(getattr(pytweening, i) for i in dir(pytweening) if isinstance(getattr(pytweening, i), types.FunctionType))
	            if "tween function" in i.__doc__ ]

def TweenWrapper(TweeningFunction, Progress, LowerBound, UpperBound):
	"""Call a given Tweening Function with given progress and return a value inside the bound (both inclusive)"""
	TweenValue = TweeningFunction(Progress)
	return (TweenValue * (UpperBound - LowerBound)) + LowerBound

def MegaTweenWrapper(TweeningFunction, Steps, LowerBound, UpperBound):
	"""Return a list returned by calling TweenWrapper() for given n Steps"""	
	ReturnValues = []
	Iterator = list(range(1, Steps+1)) # +1 on both sides so as to prevent 0 from popping up and causing ZeroDivisionError
	for i in Iterator:
		Progress = float(i) / max(Iterator)
		ReturnValues.append(TweenWrapper(TweeningFunction, Progress, LowerBound, UpperBound))
	return ReturnValues
