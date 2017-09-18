# encrypted_vars

## Synopsis

HAdeploy allow most of the variable to be encrypted. This feature rely on the [Ansible Vault](http://docs.ansible.com/ansible/playbooks_vault.html) mechanism.

All encrypted values must be set under one or several `encrypted_vars` token, and their usage must follow a specific pattern. See the example below.

## Attributes

Attributes are variables name.

## Example

A typical use case of encryption is to protect the`ssh_password` in a host definition. Encryption can be achived by provided the values as in the following sample:

```yaml

encrypted_vars:
  john_password: |
    $ANSIBLE_VAULT;1.1;AES256
    65626166653134326137613232323336373139393036383532333863623630363662303531306539
    6637306363343836376633353439656634613638643031660a636238323663353337313333663438
    30306234306463626338663637623563393735653237323833323064316561653237393538303762
    6363326232656461310a656631386135663764386565366566633537633665646562626236393462
    6231

- name: sr
  ssh_host: sr.cluster1.mydomain.com
  ssh_user: root
  ssh_password: "{{john_password}}"

```
Note the way the variable is provided to the ranger_password attribute: `"{{john_password}}"` (And not the usual `${john_password}`). This form is mandatory, 
as the variable resolution must be performed by Ansible, not by HADeploy. See [Variables](../../more/under_the_hood/#variables) for more info.

NB: As the encrypted value is directly provided to Ansible, which will decrypt it in memory, HADeploy itself does not perform any decryption. So, there is no risk to have a decrypted, clear value in some intermediate file.

Using this pattern, most of the values of type string can be encrypted in the depployement file.

Another use case of encryption is to protect the ranger admin password in the `ranger_relay` definition:
```yaml
encrypted_vars:
  ranger_password: |
    $ANSIBLE_VAULT;1.1;AES256
    34396662613462623565323936616330623661623065343033646136643635653430636238613962
    3537343131346462343138343064313937646366363435340a633532366162623838376436366362
    61393033343932303636653066336130616132383463373934396265306364363562613565613165
    6163613739303430650a356136353865623534643237646166393230613933396166663963633538
    3664

ranger_relay:
  host: en1
  ranger_url:  https://ranger.mycluster.mycompany.com:6182
  ranger_username: admin
  ranger_password: "{{ranger_password}}"  
  ca_bundle_local_file: cert/ranger_mycluster_cert.pem
  ca_bundle_relay_file: /etc/security/certs/ranger_mycluster_cert.pem
```


## Encrypting a value

HADeploy encryption rely on the Ansible Vault capability. So, the encryption will be performed using `ansible-vault` commmand.

Here is a simple approach to achieve this:

First, create a temporary file containing only the password (Here, the password is `admin`):

```bash
echo -n admin >/tmp/data.txt
```

It is important to ensure there is no leading or trailing control character, or white space:


```bash
hexdump -C /tmp/data.txt
00000000  61 64 6d 69 6e                                    |admin|
00000005
```

Then, you can encrypt it, using the following command:

```bash
ansible-vault encrypt </tmp/data.txt
New Vault password:
Confirm New Vault password:
$ANSIBLE_VAULT;1.1;AES256
36303764663465323835653063393330393363656263356332383930363039303662663530653561
3365366637386139333030306638633739653332336363380a623833646435393466386531616230
36396536633064663736643931313464366166663062663165333362656262626638343532393538
6562643836373164620a653835383665356233643835613066653261333561333533356638303963
3266
Encryption successful
```

You will need to provide a Vault password. This is the password you will have to provided later, on each launch of HADeploy.

Now, you may cut and paste the result as your `encrypted_vars.ranger_password` value, as shown on the top of this page. And be sure:

* Indentation is the same for all lines.
* Indentation is only made of space (No tab).
* There is no space, or white space at the end of the line.

If you don't follow these recommendation, we may have some cryptic error messages, such as:

```bash
fatal: [en1]: FAILED! => {"failed": true, "msg": "Unexpected templating type error occurred on ({{ rangerPassword }}): Non-hexadecimal digit found"}
```

And, of course, don't forget to cleanup the file which contains the password in clear text.

```
rm /tmp/data.txt
```

## Launching HADeploy with encrypted values

> Do not mistake this feature with the vault password you may need to provide when accessing an Ansible inventory ([see here](../plugins_reference/ansible_inventories/ansible_inventories)). 
There is no relationshipt between these two passwords. They act at different level.

If you launch HADeploy on file containing encrypted value, you will need to provide a password. Otherwise you will have an error like the following: 

```bash
The offending line appears to be:

  vars:
      rangerPassword: !vault |
                      ^ here
```

First approach is to enter this password on each launch. For this, simply add the option `--askVaultPassword` on the command line.

```bash
hadeploy --src infra/mycluster.yml --src app.yml --askVaultPassword  --action DEPLOY
....
Vault password:
```

Another approach is to provide this password in a file. The password must be a string stored as a single line of the file.

Then use the option `--vaultPasswordFile` to provide the path on this file:

```bash
hadeploy --src infra/mycluster.yml --src app.yml --vaultPasswordFile infra/vault_password.txt  --action DEPLOY
```

Ensure permissions on the file are such that no one else can access your key and do not add this file to source control.




