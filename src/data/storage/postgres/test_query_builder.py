from textwrap import dedent

from data.storage.postgres.query_builder import Query


def test_create_query_select_from():
    query = Query().SELECT("column_one", "column_two").FROM("table")
    assert str(query).strip() == dedent(
        """
        SELECT
            column_one,
            column_two
        FROM
            table
        """.rstrip().removeprefix("\n"),
    )


def test_create_query_select_from_with_filter():
    pass
    query = Query().SELECT("column_one").FROM("table").WHERE("column_one > 0", "column_two IS NOT NULL")
    assert str(query).strip() == dedent(
        """
        SELECT
            column_one
        FROM
            table
        WHERE
            column_one > 0 AND
            column_two IS NOT NULL
        """.rstrip().removeprefix("\n"),
    )


def test_create_query_select_from_with_orders():
    query = Query().SELECT("column_one", "column_two").FROM("table").ORDER_BY("column_one ASC", "column_two DESC")
    assert str(query).strip() == dedent(
        """
        SELECT
            column_one,
            column_two
        FROM
            table
        ORDER BY
            column_one ASC,
            column_two DESC
        """.rstrip().removeprefix("\n"),
    )


def test_create_query_select_from_with_group_by():
    query = Query().SELECT("column_one", "column_two").FROM("table").GROUP_BY("column_one")
    assert str(query).strip() == dedent(
        """
        SELECT
            column_one,
            column_two
        FROM
            table
        GROUP BY
            column_one
        """.rstrip().removeprefix("\n"),
    )


def test_create_query_select_from_with_joins():
    query = (
        Query()
        .SELECT("t.column_one", "b.column_two")
        .INNER_JOIN("table_b b")
        .ON("b.column_two = t.column_two")
        .FROM("table t")
        .WHERE("t.column_one IS NOT NULL")
    )
    assert str(query).strip() == dedent(
        """
        SELECT
            t.column_one,
            b.column_two
        FROM
            table t
        INNER JOIN
            table_b b
        ON
            b.column_two = t.column_two
        WHERE
            t.column_one IS NOT NULL
        """.rstrip().removeprefix("\n"),
    )
