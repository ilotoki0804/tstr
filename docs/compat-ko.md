# tstr의 호환성

template string은 파이썬 3.14에 추가된 기능으로, 그 이하 버전에서는 기본적으로 사용할 수 없습니다.
하지만 `tstr` 라이브러리를 사용하면 이전 버전과 최신 버전 모두에서 호환되는 코드를 작성할 수 있습니다.

`Template`이나 `Interpolation` 클래스를 사용하고 싶을 때는 버전에 관계없이 `tstr`에서 직접 import하면 됩니다.

```python
from tstr import Template, Interpolation
```

만약 파이썬 3.14 이상 버전을 사용하고 있다면, 이는 `string.templatelib.Template`의 alias로 작동합니다.
반면 3.14 미만 버전에서는 `string.templatelib.Template`과 호환되는 `tstr`의 자체 구현이 import됩니다.

현재 어떤 구현이 사용되고 있는지 확인하려면 `tstr.TEMPLATE_STRING_SUPPORTED` 상수를 확인하면 됩니다.
이 값이 `True`면 네이티브 구현이, `False`면 호환 구현이 사용 중인 것입니다.

모든 tstr 내 모든 함수들과 구현은 `TEMPLATE_STRING_SUPPORTED`의 값에 따라 네이티브 구현을 사용할지 백포트를 사용할지 결정합니다.
이 모든 과정은 자동으로 이루어지기 때문에 라이브러리를 사용할 때는 둘을 굳이 구별할 필요가 없습니다.

## `generate_template()` 함수

`generate_template()` 함수(별칭 `t()`)는 문자열로부터 Template 객체를 생성합니다. 이 함수는 t-string 리터럴이 지원되지 않는 
파이썬 버전에서 특히 유용합니다. 별도의 context를 제공하지 않으면 호출자의 로컬 변수들이 자동으로 사용됩니다.

이 함수가 가장 유용한 경우는 t-string 리터럴을 사용할 수 없는 버전에서 t-string을 생성해야 하거나,
t-string을 지원하지 않는 버전도 지원해야 하는 라이브러리 등에서 유용하게 사용할 수 있으며,
또는 비록 권장되진 않지만 t-string을 다이내믹하게 construct하고 싶은 경우에도 사용할 수 있습니다.

아래는 `generate_template()` 함수를 사용하는 예시입니다.
t-string을 사용하는 자리에 `generate_template()` (혹은 `t()`)으로 대체해 사용할 수 있습니다.


```python
from tstr import f, t, template_eq

name = "Alice"
template = t("Hello, {name}")
assert f(template) == "Hello, Alice"

# t-string 문법과 동일한 결과
assert template_eq(template, t"Hello, {name}")

# 변환 지정자, 형식 지정자, 그리고 디버그 지정자 사용 가능
template = t("My name is {name!r:>10s}.")
assert f(template) == "My name is    'Alice'."
assert template_eq(template, t"My name is {name!r:>10s}.")
assert f(t("{name = }")) == "name = 'Alice'"
```

t-string 리터럴은 interpolation에 임의의 표현식을 사용해 평가되지만, `generate_template()`에서는 `use_eval` 매개변수를 달리해 동작을 변경할 수 있습니다.
`use_eval` 매개변수가 `False`인 경우, context에 제공된 변수만 사용할 수 있습니다. `True`로 설정하면 표현식도 평가할 수 있습니다.

`generate_template()`의 두 번째 매개변수는 `context`입니다. 이 `context`는 mapping으로 변수의 값을 조절해서 
`context`에서 값을 찾을 수 없고 `use_eval`이 False인 경우 해당 expression을 포함한 KeyError를 raise합니다. 이는 `str.format`의 동작과 동일합니다.

```python
from tstr import t

# 단순 변수 사용
template = t("The number is {num}!", {"num": 200}, use_eval=False)  # context에 저장된 `num`이 사용되었으므로 정상 작동

# 표현식 사용
template = t("The number is {num * 20}!", {"num": 200}, use_eval=False)  # 오류 발생: 표현식 평가 불가

# use_eval=True로 설정하면 표현식 평가 가능
template = t("The number is {num}!", {"num": 200}, use_eval=True)  # 물론 단순 변수도 사용할 수 있습니다.
template = t("The number is {num * 20}!", {"num": 200}, use_eval=True)  # 정상 작동: "The number is 4000!"
```

<!-- 이때 '복잡한 표현식'은 `str.format`에서 사용할 수 없는 표현식을 의미합니다.
달리 말해, `str.format`에서도 사용할 수 있는 attribute를 접근하는 등의 '간단한' 표현식은 `use_eval`을 -->

`globals` 매개변수는 `use_eval=True`일 때 `eval` 함수에 제공할 전역 네임스페이스입니다.
주로 다른 모듈에서 가져온 함수나 클래스를 표현식에서 사용할 때 필요합니다.

`use_eval` 값을 명시적으로 지정하지 않으면, `context`와 `globals` 설정에 따라 자동으로 결정됩니다.
둘 다 지정하지 않으면 `use_eval=True`로, 둘 중 하나라도 지정하면 `use_eval=False`로 설정됩니다.
이는 명시적으로 컨텍스트를 제공한 경우 보안상 안전한 기본값을 사용하기 위함입니다.

`generate_template`과 `t`는 단순히 편의를 위해 이름만 다르게 붙인 서로 같은 함수입니다.
두 함수 중 어느 것을 사용하더라도 기능은 완전히 동일하나 텍스트 리터럴에서 곧바로 template string을 생성할 때는 `t`를,
그 외의 경우에는 `generate_template`을 사용하는 것이 권장됩니다.

### 호환성과 사용성

duck typing을 사용하는 코드에서는 호환 t-string이 원활하게 작동합니다.
`isinstance()` 체크와 같이 구체적인 클래스 타입이 필요하거나 type hint를 추가하고자하는 경우에는
`tstr`에서 임포트한 `Template`과 `Interpolation`을 사용하면 됩니다.
그러면 t-string이 네이티브로 지원되는 경우에는 `string.templatelib`에서 제공하는 네이티브 타입이,
그렇지 않은 경우에는 타입이 나타납니다.

### 네이티브 t-string과의 차이점

호환 t-string을 사용할 때는 몇 가지 제한사항이 있습니다:

1. t-string 리터럴에서 `SyntaxError`가 발생하는 사례들에 대해, 호환 버전에서는 런타임에 `ValueError`가 발생하며 오류 메시지가 다를 수 있습니다.
2. 임의의 표현식을 사용할 수는 없습니다. 대표적으로 interpolation 내부에 문자열을 감쌀 때 사용했던 quote를 다시 사용했을 때 오류가 발생하는 것을 들 수 있습니다. [PEP 701](https://peps.python.org/pep-0701/)과 비슷한 상황입니다.
3. 파서의 한계로 인해 interpolation 내부에 `:`나 `!` 문자가 포함된 경우 제대로 처리되지 않습니다.

```python
# 네이티브 t-string에서는 작동하지만 generate_template()에서는 문제가 될 수 있는 예시들
template = t"Hello, {"Alice"}!"  # 리터럴에서 정상 작동
template = t("Hello, {"Alice"}!")  # 오류: t() 함수에서는 문자열이 홀로 올발라야 함
template = t('Hello, {"Alice"}!')  # 정상 작동: 외부에 사용된 quote를 내부에서 사용하지 않음

template = t"Hello, {'Alice!'}"  # 리터럴에서 정상 작동
template = t("Hello, {'Alice!'}")  # 오류: interpolation 내 '!' 문자를 사용하면 안 됨
```
