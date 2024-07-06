from yoomoney import Quickpay
quickpay = Quickpay(
            receiver="4100118737683561",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=2,
            label="a1b2c3d4e5",
            )
print(quickpay.base_url)
print(quickpay.redirected_url)