########
Concepts
########

Describing decisions
====================

There are multiple situations where you need to describe how a
submission should be evaluated and what is correct behaviour and what not.
This can include the following:

- Specify the success condition of a test case
- Trigger actions like showing warnings depending on the submission
- *Idea: Provide a formula for the allowed number of blocks (per type) a submission may use
  (requires selectors that are not implemented yet)*

This library thinks of decisions in the following way:

1. You :any:`select <Selector>` values that are currently unknown
   (as you don't know what submissions will be handed in in the future), ...
2. ... :any:`transform <Transformation>` these values with multiple operations, ...
3. ... and finally give them to a :any:`criterion <Criterion>`
   that decides if the condition is satisfied.

By using that model, this library only provides some predefined selectors,
transformations and criteria that can be plugged together in multiple ways.

The created tree of multiple different selector-, transformation- and criterion-nodes
is then transformed to a JSON representation that can be stored or sent to a server.

.. warning::

   As this tree can only contain predefined stages plugged together,
   you **can't define new functionality** for evaluating submissions
   that can not be expressed by combining the predefined stages.
   The generated JSON will be interpreted at a later point in time by
   **another program that won't know anything about your modifications**
   and deviations from the normal specification format which will
   likely just cause errors.

.. _placeholders-in-future:

Placeholders live in the future
===============================


Available decision components
=============================

.. _concept-selectors:

Selectors
---------

- :class:`Array indexing<bast3st.decisions.FutureArray>`:
  access a specific element of a :class:`FutureArray <bast3st.decisions.FutureArray>`

    - :func:`LIST("mylist")[number]<bast3st.decisions.LIST>`: select one of the items of the list `mylist` using the state after executing the program
    - :func:`INPUT[number]<bast3st.decisions.INPUT>`: select one of the inputs the submission received during the current test
    - :func:`OUTPUT[number]<bast3st.decisions.OUTPUT>`: select one of the outputs the submission received during the current test
    - :func:`RANDOMS[number] <bast3st.decisions.RANDOMS>`: select one of the random numbers the submission requested and received during the current test
- :class:`Array length<bast3st.decisions.FutureArray>`:
  number of elements in the respective :class:`FutureArray <bast3st.decisions.FutureArray>`

    - :func:`LIST("mylist").length <bast3st.decisions.LIST>`
    - :func:`INPUT.length <bast3st.decisions.INPUT>`
    - :func:`OUTPUT.length <bast3st.decisions.OUTPUT>`
    - :func:`RANDOMS.length <bast3st.decisions.RANDOMS>`
- :func:`VAR("myvar")<bast3st.decisions.VAR>`: value of a specific variable
- :func:`Value::first_capture <bast3st.decisions.Value.first_capture>`:
  :code:`value2 = value1.first_capture("^.(?P<sndLetter>).$")["sndLetter"]`
- :class:`NetworkRequest <bast3st.decisions.NetworkRequest>` (click for details)

.. _concept-transformations:

Transformations
---------------

- :func:`concat<bast3st.decisions.concat>`: :code:`concat(value1, " + ", value2)`
    
    - :mod:`t-string<string.templatelib>`-version: :code:`t"{value1} + {value2}"`

      + :mod:`t-string<string.templatelib>` templates are accepted by everyting that takes :any:`IntoValue` or :any:`IntoTextValue`
      + :mod:`t-string<string.templatelib>` templates can be converted explicitly using :any:`Value.of(t"{value1} + {value2}") <Value.of>`:
- :meth:`Value::to_lower<bast3st.decisions.Value.to_lower>`
- :meth:`Value::to_upper<bast3st.decisions.Value.to_upper>`
- :meth:`Value::trim<bast3st.decisions.Value.trim>`
- :meth:`Value::trim_start<bast3st.decisions.Value.trim_start>`
- :meth:`Value::trim_end<bast3st.decisions.Value.trim_end>`
- :func:`if_then_else <bast3st.decisions.if_then_else>`: select one of two options depending on the acceptance state of a criterion

.. _concept-criteria:

Criteria
--------

- :func:`Value::contains_text <bast3st.decisions.Value.contains_text>`:
  :code:`value1.contains_text("hello")`
- :func:`Value::contains_this_number <bast3st.decisions.Value.contains_this_number>`:
  :code:`value1.contains_this_number(42)`
- :func:`Value::contains_only_this_number <bast3st.decisions.Value.contains_only_this_number>`:
  :code:`value1.contains_only_this_number(42)`
- :func:`Value::contains_with_gaps <bast3st.decisions.Value.contains_with_gaps>`:
  :code:`value1.contains_with_gaps("42", "is greater", "24")`
- :func:`Value::matches <bast3st.decisions.Value.matches>`:
  :code:`value1.matches("(?i)a+(?-i)b+")`
- :class:`compare`: typically you can use the short-cut syntax :any:`Value`

  - :any:`compare.eq`: :code:`value1 == value2`
  - :any:`compare.neq`: :code:`value1 != value2`
  - :any:`compare.lt`: :code:`value1 <  value2`
  - :any:`compare.gt`: :code:`value1 >  value2`
  - :any:`compare.le`: :code:`value1 <= value2`
  - :any:`compare.ge`: :code:`value1 >= value2`
- :func:`if_then_else <bast3st.decisions.if_then_else>`: select one of two options depending on the acceptance state of a criterion

- Junctors

  - :func:`all_of(...) <bast3st.decisions.all_of>`:
    :code:`all_of(last_output_contains_A, last_output_contains_a, failure_explaination="Your last output should contain at least one lowercase and one uppercase a")`
  - :func:`any_of(...) <bast3st.decisions.any_of>`
    :code:`any_of(last_output_contains_A, last_output_contains_a, failure_explaination="Your last output should contain at least one a (lower or upper case)")`
  - :any:`Criterion::negate <bast3st.decisions.Criterion.negate>`
    :code:`last_output_contains_number.negate(failure_explaination="Your last output shouldn't contain any number")`


.. _catchable-errors:

Catchable errors
================

There are multiple situations in which decision entities
can encounter unexpected situations or failures.
One of the simplest can occur when selecting the first :any:`OUTPUT`
during a decision as there can be submissions that don't produce
any output at all.
As the term *Catchable errors* implies, one can still work with those
errors to procede the evaluation by *catching* them.

Normally, selectors, transformations and criteria work on the *happy path*::

                                      v catch
    (error path)       +--------------+
                      /                \
                     /                  \
    (happy path) ---+--------------------+----->
                    ^ error

When errors – that aren't severe enough to cancel the whole execution – occur,
the values move to the error path and further (normal) transformations
and criteria will be skipped to pass the error up.
By using a special method to `catch` the error, the execution can come
back to the happy path when the error is handled.

- catching for (transformed) values: :func:`Value::catch <bast3st.decisions.Value.catch>`
- catching for criteria: :func:`Criterion::catch <bast3st.decisions.Criterion.catch>`

Uncatched errors have different effects depending on the context in which they occur.

See :any:`err` for a list of available error kinds that can be catched.

.. _concept-actions:

Actions
=======

In addition to specifying if a test should pass or fail, :ref:`concept-criteria` can be used 
to trigger *actions* if there conditions are satisfied:

- generate a message that will be displayed
  to the student who has submitted a file for checking:

  - :func:`send_message<bast3st.actions.send_message>`
  - :func:`send_info<bast3st.actions.send_info>`
  - :func:`send_warning<bast3st.actions.send_warning>`
  - :func:`send_error<bast3st.actions.send_error>`

- :any:`pass_this_test_immediatly`: stop further checking of :ref:`concept-criteria`
  and mark the currently checked test as *passed*.
- :any:`fail_this_test_immediatly`: stop further checking of :ref:`concept-criteria`
  and mark the currently checked test as *failed*.
- :func:`if_then_else <bast3st.decisions.if_then_else>`: select one of two actions depending on the acceptance state of a criterion
- :func:`set_flag(key, value)<bast3st.actions.set_flag>`:

  .. note:: `set_flag` could be a way to pass arbitrary data to whoever asked the server to
     evaluate a submission. The flags from one action could maybe also be read from within
     other criteria, **but never in the criterion where it was set** as this would imply
     dependencies on the execution order of a single decision.


Test specification
==================

The top-level part of a specification is :class:`Bast3StSpec<bast3st.spec.Bast3StSpec>` which contains all categories and meta information about the point of the whole exercise.
A :class:`Bast3StSpec<bast3st.spec.Bast3StSpec>` object can contain
multiple :class:`Category<bast3st.spec.Category>` objects that group
tests by logical relation.
Each :class:`Category<bast3st.spec.Category>` has multiple
:class:`MainTest<bast3st.spec.MainTest>` instances each of them being
able to hold :class:`AlternativeTest<bast3st.spec.AlternativeTest>`
objects. These objects
(aside from :class:`Bast3StSpec<bast3st.spec.Bast3StSpec>`)
should mostly not be instantiated directly but through special
functions:

- :func:`Bast3StSpec::new_category<bast3st.spec.Bast3StSpec.new_category>`
- :func:`Category::new_test<bast3st.spec.Category.new_test>`
- :func:`MainTest::new_alternative_test<bast3st.spec.MainTest.new_alternative_test>`

See the functions for required arguments. All levels support extra hook
conditions to run actions if some criterion is suffied:

- :func:`Bast3StSpec::if_criterion_then<bast3st.spec.Bast3StSpec.if_criterion_then>`
- :func:`Category::if_criterion_then<bast3st.spec.Category.if_criterion_then>`
- :func:`MainTest::if_criterion_then<bast3st.spec.MainTest.if_criterion_then>`
- :func:`AlternativeTest::if_criterion_then<bast3st.spec.AlternativeTest.if_criterion_then>`

Each of those functions specifies an *order* which decides when the
condition should be checked. The following shows a typical flow:

1. *run hooks of* :class:`specification<bast3st.spec.Bast3StSpec>`
   *that should be run before all categories*
2. process each :class:`Category<bast3st.spec.Category>`:

    3. *run hooks of* :class:`Category<bast3st.spec.Category>`
       *that should be run before all tests of this category*
    4. process each :class:`MainTest<bast3st.spec.MainTest>`:

        5. *run hooks of* :class:`MainTest<bast3st.spec.MainTest>`
           *that should be run before the actual test*
        6. evaluate the main test's :class:`Criterion<bast3st.decisions.Criterion>`
           to decide if the test should be passed 
        7. *run hooks of* :class:`MainTest<bast3st.spec.MainTest>`
           *that should be run after the main test but before the*
           *alternative tests*
        8. **If the main test failed**, process each
           :class:`AlternativeTest<bast3st.spec.AlternativeTest>`
           in order until one passes or all were tried:
            
            9. *run hooks of*
               :class:`AlternativeTest<bast3st.spec.AlternativeTest>`
               *that should be run before the alternative test*
            10. evaluate the alternative test's :class:`Criterion<bast3st.decisions.Criterion>`
                to decide if the test should be passed.
                (if so, run 11 but proceed to 12 without trying 8 again)
            11. *run hooks of*
                :class:`AlternativeTest<bast3st.spec.AlternativeTest>`
                *that should be run before the alternative test*

        12. *run hooks of* :class:`MainTest<bast3st.spec.MainTest>`
            *that should be run after the main test and after the*
            *alternative tests*

    13. *run hooks of* :class:`Category<bast3st.spec.Category>`
        *that should be run after all tests of this category*

14. *run hooks of* :class:`specification<bast3st.spec.Bast3StSpec>`
    *that should be run after all categories*

.. note::

   This order of hook execution is only important if you rely on
   results from other stages being present, like when you set
   flags or change the global state in other means.

