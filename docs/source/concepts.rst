########
Concepts
########

Describing decisions
====================

There are multiple situations where you need to the describe how a
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


Selectors
---------

- :class:`Array indexing<bast3st.decisions.FutureArray>`:
  access a specific element of a :class:`FutureArray <bast3st.decisions.FutureArray>`

    - :func:`LIST("mylist")[number]<bast3st.decisions.LIST>`
    - :func:`INPUT[number]<bast3st.decisions.INPUT>`: select one of the inputs the submission received during the current test
    - :func:`OUTPUT[number]<bast3st.decisions.OUTPUT>`: select one of the outputs the submission received during the current test
- :class:`Array length<bast3st.decisions.FutureArray>`:
  number of elements in the respective :class:`FutureArray <bast3st.decisions.FutureArray>`

    - :func:`LIST("mylist").length <bast3st.decisions.LIST>`
    - :func:`INPUT.length <bast3st.decisions.INPUT>`
    - :func:`OUTPUT.length <bast3st.decisions.OUTPUT>`
- :func:`VAR("myvar")<bast3st.decisions.VAR>`: value of a specific variable


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

Criteria
--------

- :func:`Value::contains_text <bast3st.decisions.Value.contains_text>`:
  :code:`value1.contains_text("hello")`
- :func:`Value::contains_this_number <bast3st.decisions.Value.contains_this_number>`:
  :code:`value1.contains_this_number(42)`
- :func:`Value::contains_only_this_number <bast3st.decisions.Value.contains_only_this_number>`:
  :code:`value1.contains_only_this_number(42)`
- :class:`compare`: typically you can use the short-cut syntax :any:`Value`

  - :any:`compare.eq`: :code:`value1 == value2`
  - :any:`compare.neq`: :code:`value1 != value2`
  - :any:`compare.lt`: :code:`value1 <  value2`
  - :any:`compare.gt`: :code:`value1 >  value2`
  - :any:`compare.le`: :code:`value1 <= value2`
  - :any:`compare.ge`: :code:`value1 >= value2`

- Junctors

  - :func:`all_of(...) <bast3st.decisions.all_of>`:
    :code:`all_of(last_output_contains_A, last_output_contains_a, failure_explaination="Your last output should contain at least one lowercase and one uppercase a")`
  - :func:`any_of(...) <bast3st.decisions.any_of>`
    :code:`any_of(last_output_contains_A, last_output_contains_a, failure_explaination="Your last output should contain at least one a (lower or upper case)")`
  - :any:`Criterion::negate <bast3st.decisions.Criterion.negate>`
    :code:`last_output_contains_number.negate(failure_explaination="Your last output shouldn't contain any number")`
