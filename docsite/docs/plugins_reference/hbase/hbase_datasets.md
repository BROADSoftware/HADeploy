# hbase_datasets

## Synopsis

Provide a list of datasets to upload in HBase tables 

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | --- | ---
table|yes|The table to populate
namespace|yes|The name of the HBase namespace where the table is.
src||The file containing the data to load in the table. May be in the form:<ul><li>`http://....` for fetching the file from a remote http server</li><li>`https://...` for fetching the file from a remote https server</li><li>`file://...` for fetching the file locally, from one of the folder provided by the [`local_files_folders:`](../files/local_files_folders) list</li><li>`file:///...` for fetching the file locally, with a absolute path on the HADeploy node.</li><li>`tmpl://...`  Source is a template, which will be processed by Ansible/Jinja2 mechanism. Template will be fetched locally, from one of the folders provided by the [`local_templates_folders:`](../files/local_templates_folders) list</li><li>`tmpl:///...` Same as above, except source template will be fetched from the HADeploy node with an absolute path.</li></ul>The file format is described below
delRows|no|See below.<br>Default: `no`
delValues|no|See below.<br>Default: `no`
dontAddRow|no|See below.<br>Default: `no`
dontAddValue|no|See below.<br>Default: `no`
updValues|no|See below.<br>Default: `no`
validate_certs|no|Boolean; In case of src: `https://...` Setting to false, will disable strict certificate checking, thus allowing self-signed certificate.<br>Default: `yes`
force_basic_auth|no|Boolean; In case of `src: http[s]://...` . The underlying module only sends authentication information when a webservice responds to an initial request with a 401 status. Since some basic auth services do not properly send a 401, logins will fail. This option forces the sending of the Basic authentication header upon initial request.
url_username|no|String; In case of `src: http[s]://...`. The username for use in HTTP basic authentication. This parameter can be used without url_password for sites that allow empty passwords.
url_password|no|String; In case of `src: http[s]://...`. The password for use in HTTP basic authentication
no_remove|no|Boolean: Prevent this dataset to be deleted from the table when HADeploy will be used in REMOVE mode.<br>Default: `no`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Example
```yaml
hbase_datasets:
  - table: hbload1
    namespace: default
    src: file://dataset1.json
    updValues: yes
```
## Action on pre-existing data

If the HBase table already contains some data, the default behavior is 'Just add, don't delete, don't modify'. Options are provided to modify such behavior.

* Un-existing row will be added. (Un-existing means there is no row with this rowKey present in the table). If you want to prevent this, set dontAddRow.
* Row existing in the table but not in the dataset file will NOT be deleted. If you want to delete them, set delRows.
* If a row already exists and is identical, it will not be modified.
* If a row exists in the table, but the input dataset provide more columns:values, the missing column:value will be added. If you want to prevent this, set dontAddValue
* If a row exists, but the input file provide less column:value, the column:value will NOT be deleted. If you want to delete them, set delValues.
* If a row exists but some value for an existing qualifier differs from the one in the input file, value will NOT be updated. If you want to update them, set updValues.

If you set this switches combination:
```yaml
dontAddRow: yes
dontAddValue: yes
```
Then, this operation will not modify the table

If you set this switches combination:
```yaml
delRows: yes
delValues: yes
updValues: yes
```
Then, the content of the table will be adjusted to be fully identical to the content of the dataset file.

## File format

The file format used by hbase_datasets is a json with the following form:
```json
{
    { "rowKey1": { "colFamily1": { "qualifier1": "value1", ...}, "colFamily2": { ... }, ...}, 
    { "rowKey2": { "colFamily1": { "qualifier1": "value1", ...}, "colFamily2": { ... }, ...},
    ...
} 
```
For example:
```json
{
    "000000": { "id": { "fname": "Delpha", "lname": "Dickinson", "prefix": "Mr.", "reg": "000000" }, "job": { "cpny": "Barton, Barton and Barton", "title": "Human Branding Officer" } }
   ,"000001": { "id": { "fname": "Alvina", "lname": "Schulist", "prefix": "Dr.", "reg": "000001" }, "job": { "cpny": "Hilll, Hilll and Hilll", "title": "Investor Brand Coordinator" } }
   ,"000002": { "id": { "fname": "Berniece", "lname": "Bahringer", "prefix": "Mrs.", "reg": "000002" }, "job": { "cpny": "Eichmann-Eichmann", "title": "District Paradigm Coordinator" } }
}
```

### Binary representation

Internally, HBase does not handle String, but byte[]. So, there is a need to represent binary data in string representation. Choice has been made to use the escape convention of the HBase function `Bytes.toByteBinary()` and `Bytes.toStringBinary()`, using the `'\xXX'` notation, where `XX` is the hexadecimal code of the byte.
Note, the `'\'` itself must be escaped. For example, the binary code 1 will be represented by `"\\0x01"`

### Fetch dataset from an existing file

It can be useful to create an initial dataset file from data already existing in an HBase file.

You can use the `hbdump` tool you will find at 

[https://github.com/BROADSoftware/hbtools](https://github.com/BROADSoftware/hbtools)

Note than, internally, HADeploy uses the `hbload` tool to load these dataset.

Also, note the `hbdump` output will not escape printable characters, so, for example `"7000003"` and `"\\x37000003"` represents the same byte, as `x37` is the hexadecimal code of the character `'7'`. Same for `"\\x2E000007"` and `".000007"`

## Limitations

* `hbase_datasets` does not dynamically create HBase column family. All column family referenced in the input file must be already defined in the HBase table. Or an error will be generated.
* `hbase_datasets` does not handle HBase cell's timestamp.
* `hbase_datasets` is not intended to work on 'big' dataset. It is intended to be use in application deployment where some tables need to be populated with an initial bunch of data. It will fully load its dataset in memory, thus limiting the volume it will be able to manage.

 
