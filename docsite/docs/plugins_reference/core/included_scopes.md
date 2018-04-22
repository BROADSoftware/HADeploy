# included_scopes

## Synopsis

Allow definition of a list of 'scope' which will be the only ones included in the processing.

An empty, or unexisting list will be interpreted as 'all scopes', this full processing.

Same information can also be provided on the command line, using the `--scope` option. In such case, the command line provided scope(s) will fully override this value.
In other terms, only the command line provided scopes will be included in the processing. 

More information on this feature in a [specific chapter](../../more/altering_scope)

## Example

```yaml
included_scopes:
- hbase
- hive 
```
Only HBase and Hive related operations will be performed.