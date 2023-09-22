def debug_main():
    def fib(n: int) -> int:
        if n == 0:
            return 0
        if n == 1:
            return 1
        return fib(n - 1) + fib(n - 2)

    x = fib(2)
    fib(x)

if __name__ == '__main__':
    debug_main()
