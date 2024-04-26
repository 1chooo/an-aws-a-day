# An AWS a Day - AWS Certificate Preparation Series

Develop a Line bot using AWS Lambda Functions and `linebot.v3` library, utilizing `Python 3.12` runtime. 

> [!IMPORTANT]
> Note that `Python 3.12` operates on an **Amazon Linux 2023 Amazon Machine Image (AMI)**. Hence, ensure the creation of the layer on an **Amazon Linux 2023 OS**. [^3]


## Create `Lambda Function` Layer

### Create `line-bot-sdk` Layer [^3]

```shell
$ mkdir -p lambda-layer/python
$ cd lambda-layer/python
$ pip3 install --platform manylinux2014_x86_64 --target . --python-version 3.12 --only-binary=:all: line-bot-sdk
```

### or With shell script
```shell
$ ./scripts/build_layer.sh
```

### or just click the link below to download the `line-bot-sdk` layer

👉🏻 [Download `line-bot-sdk`](https://raw.githubusercontent.com/1chooo/aws-educate-101-line-bot/main/lambda_layers/linebot_lambda_layer.zip)

## Add Permission with s3 [^2]
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::<your-bucket-name>",
                "arn:aws:s3:::<your-bucket-name>/*"
            ]
        }
    ]
}
```

## CONTACT INFO.

> AWS Educate Cloud Ambassador, Technical Support </br>
> **Hugo ChunHo Lin**
> 
> <aside>
>   📩 E-mail: <a href="mailto:hugo970217@gmail.com">hugo970217@gmail.com</a>
> <br>
>   🧳 Linkedin: <a href="https://www.linkedin.com/in/1chooo/">Hugo ChunHo Lin</a>
> <br>
>   👨🏻‍💻 GitHub: <a href="https://github.com/1chooo">1chooo</a>
>    
> </aside>

## License
Released under [MIT](./LICENSE) by [Hugo ChunHo Lin](https://github.com/1chooo).

This software can be modified and reused without restriction.
The original license must be included with any copies of this software.
If a significant portion of the source code is used, please provide a link back to this repository.

[^1]: [使用 .zip 封存檔部署 Python Lambda 函數](https://docs.aws.amazon.com/zh_tw/lambda/latest/dg/python-package.html)
[^2]: [Policies and Permissions in Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html?icmpid=docs_amazons3_console)
[^3]: [How do I resolve the "Unable to import module" error that I receive when I run Lambda code in Python?](https://repost.aws/knowledge-center/lambda-import-module-error-python)
