from flask import Flask, request, render_template
from sympy import Matrix, lcm, gcd
from functools import reduce

app = Flask(__name__)

# Original Logic
def parse_compound(compound):
    elements = {}
    i = 0
    while i < len(compound):
        if compound[i].isupper():
            element = compound[i]
            i += 1
            while i < len(compound) and compound[i].islower():
                element += compound[i]
                i += 1
            num = ''
            while i < len(compound) and compound[i].isdigit():
                num += compound[i]
                i += 1
            elements[element] = elements.get(element, 0) + (int(num) if num else 1)
        else:
            raise ValueError(f"Invalid format in compound: {compound}")
    return elements

def balance_equation(reactants, products):
    all_compounds = reactants + products
    element_set = set()

    parsed_compounds = []
    for compound in all_compounds:
        parsed = parse_compound(compound)
        parsed_compounds.append(parsed)
        element_set.update(parsed.keys())

    element_list = list(element_set)
    matrix_rows = []

    for element in element_list:
        row = []
        for i, compound_dict in enumerate(parsed_compounds):
            count = compound_dict.get(element, 0)
            row.append(count if i < len(reactants) else -count)
        matrix_rows.append(row)

    matrix = Matrix(matrix_rows)
    nullspace = matrix.nullspace()
    if not nullspace:
        return "Error: Cannot balance the equation."

    solution = nullspace[0]
    denominators = [term.q for term in solution]
    multiple = lcm(denominators)
    coeffs = [abs(int(multiple * val)) for val in solution]

    factor = reduce(gcd, coeffs)
    coeffs = [c // factor for c in coeffs]

    lhs = ' + '.join(f"{coeffs[i]}{reactants[i]}" for i in range(len(reactants)))
    rhs = ' + '.join(f"{coeffs[i+len(reactants)]}{products[i]}" for i in range(len(products)))
    return f"{lhs} → {rhs}"

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        reactants = request.form["reactants"].replace(" ", "").split("+")
        products = request.form["products"].replace(" ", "").split("+")
        try:
            result = balance_equation(reactants, products)
        except Exception as e:
            result = f"Error: {e}"
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
