class Rectangle:
    """
    A Rectangle class that can be iterated over to get its
    length and width in a specific dictionary format.
    """
    def __init__(self, length: int, width: int):
        self.length = length
        self.width = width

    def __iter__(self):
        """
        Makes the Rectangle instance iterable.
        Yields length, then width, in the specified format.
        """
        yield {'length': self.length}
        yield {'width': self.width}

if __name__ == "__main__":
    print("Creating a Rectangle(10, 5)")
    rect = Rectangle(length=10, width=5)

    print("\nIterating over the rectangle instance:")
    for dimension in rect:
        print(dimension)

    # You can also convert it to a list
    print("\nConverting iterator to list:")
    dimensions_list = list(rect)
    print(dimensions_list)
