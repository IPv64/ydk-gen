Errors and Exceptions
=====================

Contains types representing the Exception hierarchy in YDK.

.. py:exception:: ydk.errors.YPYError

	Bases: :exc:`exceptions.Exception`
	
	Base Exception for YDK Errors.

.. py:exception:: ydk.errors.YPYDataValidationError

	Bases: :exc:`ydk.errors.YPYError`
	
	Exception for Client Side Data Validation.
	
	Type Validation.
	
	Any data validation error encountered that is related to type validation encountered does not
	raise an Exception right away.
	
	To uncover as many client side issues as possible, an i_errors list is injected in the parent entity of
	any entity with issues. The items added to this i_errors list captures the object types that caused
	the error as well as an error message.

.. py:exception:: ydk.errors.YPYModelError

	Bases: :exc:`ydk.errors.YPYError`
	
        Exception for Client Side Data Validation

        Any data validation error encountered that is related to type
        validation encountered does not raise an Exception right away.

        To uncover as many client side issues as possible,
        an i_errors list is injected in the parent entity of any entity
        with issues. The items added to this i_errors list captures the
        object type that caused the error as well as an error message.

.. py:exception:: ydk.errors.YPYServiceProviderError

	Bases: :exc:`ydk.errors.YPYError`
	
        Exception for Service Provider side validation and communication errors.

.. py:exception:: ydk.errors.YPYServiceError

	Bases: :exc:`ydk.errors.YPYError`
	
        Exception for Service side errors.
