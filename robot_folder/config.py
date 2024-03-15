def get_variables(sbs_key, user_pass_adm, user_pass_stp, user_pass_atd):
    variables = {"SUBSCRIPTION-KEY": sbs_key,
                 "AUTH_USER_ADM": {"username": "renan642@gmail.com", "password": user_pass_adm},
                 "AUTH_USER_STP": {"username": "renan642@hotmail.com", "password": user_pass_stp},
                 "AUTH_USER_ATD": {"username": "qatracktrace@hotmail.com", "password": user_pass_atd}}
    return variables