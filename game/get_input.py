"""Custom function for getting user input

Created on 2025.01.15
@author: Jakub
"""


def get_input(desired_type: type=str, check_bounds=False,
              bounds: tuple[float | int | None]=(None, None),
              prompt: str="> ") -> ...:
    """Get input from the user, cast it to the correct type and check that it's
    within bounds.

    No bounds by default.
    """
    while True:
        raw_in = input(prompt)

        try:
            typed_in = desired_type(raw_in)
        except ValueError:
            continue

        # check bounds
        if bounds != (None, None):
            if desired_type == int or desired_type == float:
                value = typed_in
            else:
                try:
                    value = len(typed_in)
                except:
                    raise TypeError(f"Cannot check bounds of an instance of {desired_type}")
                    value = None

            # Lower bound
            if bounds[0] is not None:
                if value < bounds[0]:
                    # discard out-of-bounds value
                    continue

            # Upper bound
            if bounds[1] is not None:
                if value > bounds[1]:
                    # discard out-of-bounds value
                    continue

        return typed_in

if __name__ == "__main__":
    pass