Application Snow is short for 'snowflake', the type of hierarchical data
modeling that this application supports, so-named in various
literature on hierarchical relational design.
It does not allow recursion, which is not needed anyway.

This application allows users to create their own arbitrary snowflake hierarchies,
here in relation snow_genra, each of which is supposed to correspond to a nested data structure such as an
XML document, JSON structure, YAML structure, or the like.

This application allows the user to create a genre (schema) to define all
the relational tables in any snowflake hierarchy they chose to create via
the web interface.

See table models.py and note similarities with xsd schema descriptions, facets,
etc. Basic stuff: https://www.w3schools.com/xml/schema_facets.asp
and see other pages in this set.
-
Note: Consider to assign/reserve special field name 'snowflake_text'
or similar, in an output template. Can let each of multiple applicable
templates to a given snowflake to specify a special
custom fieldname for every relation in the snowflake, so that when that
template is applied to produce output, when it matches a
snowflake relation field name, the corresponding db value will
be written/ expressed as the xml node text rather than a named xml tag attribute.
