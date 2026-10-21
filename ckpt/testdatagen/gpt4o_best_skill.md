Generate test data for the given field.

Output a markdown table.

Include some valid and invalid test data.

Ensure the table includes a minimum of 3 positive examples for each validation category and systematically covers all boundary values, negative cases, null/empty values, and format violations.

Ensure your markdown table includes:

- **Positive Tests**: Provide sufficient valid cases that satisfy all field validations. Include a minimum of 3 examples for each validation category.
- **Negative Tests**: Include a variety of invalid test cases that violate different field validations (e.g., special characters, incorrect format, length violations, null/empty values in mandatory fields, etc.). Ensure systematic coverage of format violations.
- **Boundary Tests**: Cover edge cases for minimum and maximum input boundaries, if applicable (e.g., shortest valid input, longest valid input, and just outside valid ranges). Include numerical range edges and length constraints for alphanumeric fields.

### Additional Guidelines
- For numeric fields, include valid positive values within the range, edge cases at the boundaries, and invalid cases outside the range.
- For alphanumeric fields, include valid combinations within constraints, edge cases near length boundaries, and invalid inputs violating format rules.
- For mandatory fields, explicitly test null, empty, and whitespace values.
- Ensure representation of special characters in invalid cases.
