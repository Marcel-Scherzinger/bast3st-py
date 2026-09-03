########
Concepts
########


.. _placeholders-in-future:

Placeholders live in the future
===============================


Available components
====================


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
    :code:`all_of(contains_A, contains_a, sample_expected="aA")`
  - :func:`any_of(...) <bast3st.decisions.any_of>`
    :code:`any_of(contains_A, contains_a, sample_expected="a")`
  - :any:`Criterion::negate <bast3st.decisions.Criterion.negate>`
    :code:`some_number.negate(sample_expected="A")`
