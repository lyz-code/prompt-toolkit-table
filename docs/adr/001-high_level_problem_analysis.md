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
* Create a `Table` widget that has a new content control similar to
    `FormattedTextControl` to manage the row data.

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

It worked fine, until I saw that the buffer was not scrollable, I thought of two
solutions:

* Use a ScrollablePane.
* Use pagination

### Use a ScrollablePane

I saw [this
issue](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1065),
where @jonathanslenders pointed me to `ScrollablePane`. It works perfect and now
we can scroll, but I'm not yet sure why is it [breaking the
styles](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1513).

### Use pagination

We could create the `n` and `p` bindings to move to the next page of tasks, it's
less user friendly than scrolling but if it allows us to see all the content, it
can be a first approach until scroll works.

It doesn't look easy, because the `Table` component doesn't know the
`max_height` of the screen. The `get_visible_focusable_windows` method of the
layout returns which windows are shown, and the `get_focusable_windows` returns
all of the interesting ones. This is not very helpful though because even if you
call `focus` on a window that is not visible, it won't display it. So I don't
know how could I replace the visible rows, for the ones hidden.

## Creating an `UIControl` to manage the content

`VSplit` and `HSplit` are `Container` objects, they arrange the layout and can
split it in multiple regions, but they don't manage the content. The `UIControl`
objects do it, such as `BufferControl` and `FormattedTextControl`.

Given that we want to format the content in a very specific way, it looks that
it makes more sense to create a new `UIControl` child to give it's contents to
the containers.

As the `UIControl` needs to be linked to a `Window`, and it is able to manage
the scrolling, we can play with the width inside the control to give the exact
rows, but let the `Window` manage the scrolling of the contents.

The `Table` then will become a widget, as they are reusable layout components
that can contain multiple containers and controls. It will have a window with
the table control, and other windows for the header, separators and possible
command lines.

This idea follows the guidelines of the developer in [this
issue](https://github.com/prompt-toolkit/python-prompt-toolkit/issues/872) when
another developer asked how to print charts.

> A good starting point is the FormattedTextcontrol, see:
> https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/prompt_toolkit/layout/controls.py#L220.
>
> The important method there is create_content, which receives width and height,
> but they are not passed to _get_formatted_text_cached in there.
>
> Maybe you can override some methods of this class, or create a custom UIControl
> that does the job?
>
> The UIControl should still be wrapped in a Window, but in this case, you won't
> need the text wrapping or scrolling functionality of the window, as the
> UIControl should generate the content that fits exactly.

After reviewing `UIControl` and `FormattedTextcontrol`, I'm going to start
inheriting from `FormattedTextcontrol` because it already does a lot of what
I need to do.

As we need to specify the `self.text` initially, we're going to first return the
preferred distribution, as if there was no limit in the width, assuming that
each time the `create_content` is called, the `self.text` will be overwritten
for the given `width`.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
