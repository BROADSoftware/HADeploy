# exit_on_fail

## Synopsis

A boolean flag. 

* If `yes`, all processing will exit on first failure.
* If `no`, if an host fail, it will be excluded. But the processing will continue on other hosts.

Default value: `yes

## Example

```yaml
exit_on_fail: No
```