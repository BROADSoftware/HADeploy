# excluded_scopes

## Synopsis

Allow definition of a list of 'scope' which will be excluded of the processing.

Same information can also be provided on the command line, using the `--noScope` option. In such case, the command line provided scope(s) will added to this list.

More information on this feature in a [specific chapter](../../more/altering_scope)

## Example

```yaml
excluded_scopes:
- ranger 
```

All ranger related operations will not be performed. This may be used to be inserted in the infrastructure fragment of a cluster without Ranger. 