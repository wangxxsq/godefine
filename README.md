# Godefine


replace marco in template,and generate a new go file

## License

![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)


## Get Start


we have a template file such as **"sample.go.template"**

it's contains code like:

```go
const Foo =  ${foo} // foo??? no idea @default="simple";
const Bar =  ${bar} // some bar...whatever @default=1231;
```

run script:

```bash
godefine.py -t sample.go.template -o sample.go 
```

sample.go:

```go
const Foo =  "simple" // foo??? no idea @default="simple";
const Bar =  1231 // some bar...whatever @default=1231;
```

## Template Syntax

go define will replace '${something}' with the value user provide.

if var's value not specified, `godefine` will look for the `default value` 
in the comment after `//`

default value should apply syntax as follows : '@default=your value;'  


## Advance

### pass vars from command-line (Simple, but `not suggest` :bangbang:)

pass your custom vars after `-v` option


```bash
godefine.py -v foo=11 bar=222 -t sample.go.template -o sample.go 
```

this way is not suggested.
if your value has an escape for some special char,
it's hard to handle with it.

### use vars form specified file (Suggest :smirk: :thumbsup:)

define your vars in `config.in`

```ini
foo=abc 112 333
bar=whatever
```

```bash
godefine.py -iv config.in -t sample.go.template -o sample.go 
```

as you can see ,foo's value has some `escape` char.

`godefine` script will handle them correctly.

### error handling :interrobang:

if you forgot to assign any one vars ,an error will be raised.

anyway, you still want to generate output, `-f` will be useful.

if `-f` applied, any error will be ignored,
the var who not assigned with value,will keep itself original state 
.
