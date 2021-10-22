Date: 2021-10-22

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We'd like to display data in a table in a prompt toolkit component, with the
next features:

* The input to the component should be either a list of pydantic objects, a list
    of lists of strings, or a list of dictionaries with the data.
* The header of the data is shown on top visually apart from the data
* The user can navigate through the table lines with vim like movements (`j`,
    `k`, `c-u`, `c-d`)
* If the number of rows is too big to fit the screen, a scrollbar will appear in
    the right and the user should be able to scroll down and up. The header
    should be fixed on top.
* The selected row should be highlighted (similar how `alot` does it).

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
In theory it could be done at different levels of abstraction:

* Create a `Table` class that inherits from `HSplit` and that has `VSplit` for
    rows.
* Create a `Table` class that inherits from `HSplit` that has a new control
    similar to `FormattedTextControl` to manage the row data.

## Using `VSplit` to manage the rows

This approach has [a proof of concept pull
request](https://github.com/prompt-toolkit/python-prompt-toolkit/pull/724) in
the prompt toolkit repo. You're able to pass the object a list of lists of prompt toolkit
components such as `TextArea`, `Button` or `Label`, which gives you a lot of
flexibility when creating tables with different row composition. On our use case
you'd have to build the `table` based on the values passed to the component,
which is something that the component should do.

Another problem it has is that it rewrites a lot of the code of `HSplit` and
`VSplit`. These facts in addition that I didn't fully understand the PR code,
and that I wanted to understand better how prompt toolkit components work, made
me do a new implementation using this method.

I created a `Table` object that inherited from `HSplit`, created
a `_set_row_widths` method that calculated the desired size of each cell based
on the width of the buffer, and set it in the dimensions of the rows.

It also guessed the header from the contents of the data for each of the cases.

Then the data of each row was passed to `_Row`, a class inherited from `VSplit`
that set the style of the focused line, created a row of `Window`s with
a `FormattedTextControl` component for each row, with only the first one
focusable.

It worked fine, until I saw that the buffer was not scrollable, then I saw [this
issue](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1065),
where @jonathanslenders pointed me to `ScrollablePane`.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
