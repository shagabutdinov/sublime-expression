
def call(a = 0, b = 0, arg = 0)
  return (a + b) * arg
end

# first argument will be changed
puts call(0, 2, 3)

# last argument will be changed
puts call(1, 2, 0)

# everythin in parenthesis of second call will be removed
puts call(1, 2) + call()

# brackets will be removed
var = 0

puts call(var)

exit(0)