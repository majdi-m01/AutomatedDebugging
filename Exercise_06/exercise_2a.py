from debuggingbook.DynamicInvariants import TypeAnnotator

def mystery(x, y):
    if len(y) > 0:
        return x * y
    else:
        raise ValueError('len(y) <= 0')
        

def test_mystery():
    mystery(1, 'test')
    mystery(-1, 'test')
    

def run() -> TypeAnnotator:
    # TODO
    with TypeAnnotator() as type_annotator:
        test_mystery()
    return type_annotator


if __name__ == '__main__':
    print(run().typed_function('mystery'))
