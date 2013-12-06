## -- encoding: utf-8 -
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.3.9/d3.js" charset="utf-8"></script>
<style type="text/css">
text.title {
  font-size: 22px;
}

.day {
  fill: #fff;
  stroke: #000;
  stroke-opacity: .1;
}

path.month {
  fill: none;
  stroke: #000;
  stroke-width: 2px;
}

.year {
   display: block;
}

#years {
  text-align: center;
}

#legend {
  float: right;
}

select {
  width: 350px;
}

</style>
<div id="legend">
<div id="colorpanel"></div>
<div id="slider"></div>
</div>

<div>
  <div>GPS-tracker: ${query['tracker_id']}, </div>
  <div>Time range: ${query['start'].strftime('%Y-%m-%d %H:%M:%S')} - ${query['end'].strftime('%Y-%m-%d %H:%M:%S')} (Timezone is <a href="http://en.wikipedia.org/wiki/Coordinated_Universal_Time">UTC</a>)</div>
  <div>Metric:
  <select>
    <option value="fixes">Nr. of GPS measurements</option>
    <option value="accels">Nr. of accelerometer measurements</option>
    <option value="distance">2D distance travelled (km)</option>
    <option value="maxalt">Maximum altitude (m)</option>
    <option value="avgalt">Average altitude (m)</option>
    <option value="minalt">Minimum altitude (m)</option>
    <option value="maxtemp">Maximum temperature (&deg;C)</option>
    <option value="avgtemp">Average temperature (&deg;C)</option>
    <option value="mintemp">Minimum temperature (&deg;C)</option>
    <option value="minvbat">Minimum voltage battery (V)</option>
    <option value="maxgpsinterval">Maximum interval between GPS measurements (hh:mm:ss)</option>
    <option value="mingpsinterval">Minimum interval between GPS measurements (hh:mm:ss)</option>
  </select></div>
  <div>Move mouse over day to see date and value.</div>
  <div id="years"></div>
  <div>Download raw data <a href="${files['result.csv']}">here</a></div>
</div>
</div>
<style type="text/css">
.x-colorpicker {
  border : 1px solid #98C0F4;
  background : #FFF;
}
.x-cp-rgbpicker {
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALYAAAC2CAYAAAB08HcEAAAABGdBTUEAANbY1E9YMgAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAC8gSURBVHja7F3bluM4ckzo7D/vs8+8zH6g5xM8D7Znj2c9l+4uMV2UCCqRiLwApKqqx6VzqiWRIKUWA8HIyARQfvzxR6bPx+fjL/b42/rP3//+9/WpApyNP2/f+rcM7FuC19429Bxtm3mdef9e27z3s6+9bdlr470excgI/iR+6R//+AdfPvv25+Ov+PgE9ufjE9ifj8/Hd6WxmT/jxzf4DQr4o2jb6/dC7bz38PX2//PaEPi8/Rls77aJz0Cvb+3F6/15/VuWpWzP9T0t1+X2/PLycmu7Pn/58oX+/PNP+te//kX/9Z//RT/9+0+3fT/82w/7D/3Djz98n8BOfN/0BXdeZ97Lix614zM7VtTe2q+2S0AT+D91wBbbu231HPUzVrBK8FZg73/L4/UraMsNzK9/1+v1BuL1+du3b/T169fb+VZQ//HHH/Tb//5G//znP+nn//iZfvrpp08p8vn4lCIfiYlL4llv45M++8y7iSlFFON3bRWbaokBfwe0XXxOfc36O6PX6lmycNESo2HphRvGfmXgIqTHQ3K8/r0yc1kZurL1+lfZ+uuXO2OvEuS33367yZBf/vsX+vnnn29y5MMA27gdItBOgfRk0HoAG5EnPPK9HCkBJZIErQZ28nWzDT1voGQJ1vV/tb9u2+26WQK7ArmCegXy+vwK4KJB/fLtoanXx02GvAL71//5lX755ZebHFlB/m7AFud/CnAnAFwSAZbL/pnPAh24ZDoK0uxiG6PPN1i3WGCu51O6uNAKzBagZfsVimLpvU0F8MbYrNm4nl8CW+rp9W8FdgX1CujK1hLYv//++01f//rrrzdAr69XsJe3BLb+cd8YxJFDwCd8TkpOaEB650UdQTO09x68Zg14Q1Y8npk0QxcpMaTUkNuQ3KivK9g3d6NoUN+A/eUB7F2CbMBewXtj7N/vjF3/1u01sHwqsAEznwbmLMDQZ2b/f5Zj4DHngBNRIhtPbWNL+2pW1zICMfMDrOtrrgzMwHrrgG08S4uu2VYZWzP05nxwlR/r97oB++W6ArhUUEu2vjH2Hw8psrL2+rxuW/dVK/BpwJY20BPBnAoUB4Ds2X08aJu5EkPfJQwpYd4BhHQoj0PMQK9ICdECm63X9ZklswspgWRHcVgaArsy9Gr1vb5noasxsP9sNfb6ev2rjG4B+9Pu+3x82n3PtsocliZykhzJhA2ywUbY3gv2MucpSj4grcyW1aaO7xm8ZWa2rDrN2Fp+aC29sTKjJIuUIlJ+VMaWSZfb+2/391Jb7wEj0NerzVflyPqor9e/df/ads1OPgvY9YLziYAOZc1I8BgFi57kQZraCfy8gNLTzBC0Coisf41eP5uOB7bqiJB+LtrxkLJj1cga5Fp+IGCv0kN61RrYrzKDV6Cu3+kG7i9fG529Pnb5sbkm63GbVDod2EMOwxnuSTKJwwMpZ6RlOdHxUADIjg1XAGv7gSLbGlu7HhKsFjMrkGsmro6FdjqKFSi+ApO3Z2jprcBeAV1ZegV2dUc0sFe776avv35bv0jZWXv7q8CuGryewwW2tfNZLK0DpUFmRoU7HHxXLzvHjmSgwLEIg73uWMZBpmLZy3aOBTBv85mvfxcFcLaCxA20FwVoFs+LBvR6/m3Hrc0t8Nse9fUGsDvIX+7AXr/fxqjr/vV4XoG5Pm9BY/O8WnmvgF1Ze23HG0uX12d+DRZ5yzzyn3/8eXu/bv/27X48ws8wYx8haMVeM/KAIkkAEi6ckR3SbcjqZFtelNVS0yBG5y2KictDLXR+czHkBiMdreWFADnSy/uzZmYhPfT2XVvf5MfSFTOtYC6VVbUrUhlX6OvGFZEVffvrby8N2y/L1cTAjBSZkh+K4UZAPeJNF0+HGPIjlA+a3bvTs27H7OloqduthIlqa4JX6eS9rQdyIEU8YDcA75Ixix0wruwr/eoKbAnq2/NdM5cK6Pq3snJl/vWh9XkNWM8A9iyoRwFtBo9BoMfJBAknAsAb7S6yHdssD5g7DeIIwLqdCgJNj1p50kW7HjKoFIVJFrAlE9cakaL9agns+nqTIrd2HbBfWh9b/1Vwa2DLmhMkAp4uRSayflkbLgwUFVC9hEsrRbjrUVrbchAcEmijJYfO+iGHg0FWsKjXbLgc2sJjWbch2VmC2ZEeZXM3pLVXGbVLymwA3KUIckNWUIv3Rdt/NStZHwjUj5+Zxxl7VlfLqP9EUDfsnwKqdR52dbtb3mmB3dHPCMiEWNhyQZSeLsjlkJ3Akx8S5Aq8WFtf+yzjBmgWbG4xdi10YplGl0Bezyv1s2R2Dexdhix8WIqUlIc2D+pMejwFaPg9OZYtgHkjVmaUANHnt4Cuzu+CWGllnYQxAaxS4h1LV/BKgAOGZtEeetarqyG0tCxy0oxdXgHNQnNLADfbatp9Pba6IiQKqFq2PqixB9uNgDrD0hzKEjbP48oWZe9pvQy1OdLJnpuh9ukECkqcpDS1J0WMIFGydMfOEtjrr1nBW2UHyjIKMD/YW0iRHdwv+3sE7i55I4+tD5nJ9MCd8bFHA8aMx10kYTnsSo4+9hIqpiYmPJqEjSSK3keGvChG9hBmAfV+0aZ60ouWGpv/XL3t/bhNPxe5T4J2PW67vjeTWgWPjUfNS+NjX0Rt9e5ZVz1dgbn50hXU6+tFDCC4rCC+BY/Xu49d368sX8tY19ebzcf17+Xby/353m73sbfP5fp5bIjsszV23Al4TmsnJYkVuJnfTweYqEbDkCbQFdEdypAilsxgw9KTiZQCgM26dlo5Hq4U2eqwdylS2VfqbyFBKmOz9LGl/JAjY27P151li2biDbRFsrsMECVjy2vjWX1nA7sgKTACfkuaIMAbyRO3M4D9lkSxrLzO1Qgsu4wUgVLC8aPRdlNyaC3d2HjL3hFY6OPO3pMSRHnWzT4N8poelxpbg36TIU0AWrW1HIkjlYUE9VzwOGiGZILQNwa15VtbCZcSOByWs8GqVgOC03BACrD3dLDI2saTVXcgESOtPcnSfMcpl822k3qbZVupnys7K8Dv9qDeJhi3SD2tg0k9RMx7L4Gt6lscYC98WF9H1XaW7rZckYT0sDQ2SooUA6Dedn3+AgK7Tk6Itl4aXO5fNDBVcFiPvVTtLVhd6mdLV5caCNbtQkaUyqi1UETYebvG3uo9lg3Yl6ptq7auunqvD7ne9e+qm3eNfQfrpdaHCJ29/62aenVNZA1JfV3vLDVhs7k18xo7K0O8DhCc32LpSEujqQOQexK2RcwcsLW5DTEvcD5QnQfU05bGRowtAkNu2gnJoZIxRWpwKUUE0zZMXUGqJMjDFbl2jN7IDouRv375ytLOk64HqGAMcXUWsKMCfR7Z54CdLGkBgkZPP+sOgySI50fDYwGDj0gOuA1YeAjM1b1oQC/S3vt2w9pj5GMbEuS1o7wCc+skDYCvje7uhoatjKzBK0BctJ2nLT2trUO77yCwS5S7cbKDqREsAYOj83jVdCH4HYaWQG/kjmZyECjyJMB1NV4T8Clfmre5PhqP2kjAsE6bb/XV3bYKPM3CIrgryvnogsq6D4G37qvAl6CVGhuMsvcZ2/CxM/raA7WXrfSYWmvtSGNzko3rdlSojxImuh1KgVujV8xtRsESOXpa+tiLmP6gfX+XG9WXllr8sr3vvOu6vW7b5MGyAVZuu2nsul161puDIbfVzrAec6n12Jtmpvpc/Wihueu+3au+blp965y7V17dlu0ajGvsozJkcHt2JDfSzVkpUoziJPZ0tqOn9TazjWZgJTFYWXesR7TIAQR7m4V1upyFpdcxc20jGBhKEWTzyYyjsOX2lLqQGMVg5OYcUlpsnaNIa+/+fXF2MaOz3cxjYlwhj8gMi2WdajjIvh5YrcBOZxFVUIeK/Ju6DYPBC/CfTWcjcD80ozcuyOZoLHVGJuFwLKKDXIQuLgJsi2Dv3QGprogYCbNIpt6eS3U7NidkqR1KsLl83ln6VVosddhY3S9Z+naOl2vD2JubIlj72jE2txfqOYxt1G3wwHZrMpiMu9GB3KjX4CD48xh76L1RpNR50VKrB9q6Sg1dsNS5JFJ3I2/ackVkNlLqY1XKWiRLK/+6Z3Ol03WdyRZssrAbi84owmf2sPeAzSFgT06qGHYMLxjMghowsBU8uqBXwSIpAOv9JkCjDmACfGk7gAoakfxgnZRBWUgdSArgyXM0Np/oNGbmUYG7qOAPVufpKRwie8/GHR+WIqOsDMFqBH8csLfWzsWQI1p2EJIUVnIFvOcgeGRVtISSLPr9nmhpZAc37y+1gEm9L1J+yIKoKjNEYLiILKIMMDvZIba1weJ1r96rx+8SRAaPq/xopi+77lKDpUxZ2VoGi6I6sJEjMnhkbpMy0wmaQcZ2bb9M20SHQMztOSWu7DCCQlYOhvneArsOABNSZLfpdKAoLmr3fverBdtW/e8Fj6J9U2stnh8y4qWVJkJWWIFiV8LaWXfc+tDSZvSSMlEaPQweJ7X1iLSIqvIsl4ONGmsrOEQyIsvYFkPreTpIsbVOqZNj7a2p7kUFi12VXk29V7tOMzgIGHX5aRc8anau+ytT063tg80F25JItV90Sl3sZ2H73YPJr98WGRTK/ZKtZYCog0XA0kOM7WYLDzJzpI0z5aYRc3uZQppgaBQwMrD1EDvDdnW2U2HrIW3eBZKIsVUmUduCUtsymOmpeb3r7msTiJIOKtUfSvDsGly2E1qdoj95vH7UYWbDCZqZwDFRz5GZ7sDV3UpzF5Bo0VqajeSLBjWDOhCY2lZJFtZglOy8FeyYiZlq4wmtzWgOPcG8Oysrxl4kmyO9vTFsw84qQbOstR7SAtRMrRM0krkB+8qaE1lQ1ehn768hm7bwSTN1TmM/QV9PAT0ICi39bA0aIK8jqProjqFBOWrH6tuO9T9a6zUgi2stbtRTMxgwoJ0PRgMHkN1nsevOostDx2umrm0VCxetn7UGb84v2usBAzVYjLCWiMumGDvrRSM9PGLXRVlD5HogUKNS0g6sSFrIjqCBqJwW0hJDOR6Sda3lLnRJKgHdfZFTkAkNvjO2SqlfQCJGMvkKuJvmXR0PqbtrCh0xt5xbRGpsmYQRAeqd5e9anTWz199dyDDSjF07kkzIGG7IccbOtg8KmrwkicfcI2xsgR0FnXB6McTYov2DxR8rBOgOYGnnTl/rAidVwNSxHmDpkL0lI1efHK1WoO4MocbW32+/Iyy2hlZVeuVo7uSwxs4Eg5nbRhLkHlg7UBqaGckXT2oUPUpG+9PbMDjkipBT3NRN0ysY/VKtBYedu/mpLZY2/OrH9mu3vXFFNHMLpm40tnZC5P7oT7G27DwMHJCGsZ+isWcZ2yv8dyw9DqfbBexuMLUGeANM1VGgA0KMO4N1nBiiJV0GrbGbwLNhVOM4oYMh80sGVVlD+LpzRR7+8z78S+llUuzfMXL1wD3nQzlUzfVEmcfDZasjdt6Als60N0GNbDnEwkpPFw0s0cZKtrBYKQB61PpiICYGBU+ErDjE4Lqwqb6WrJ5h6UaHXxtNXmoWUbKzzjzWNkJHdxpaZQyXOnRLtd33Idau/roITreouGHi0xk7O0/eCDt7bbOrxhYjQWMtdeEFjq1VyMRB8Ngdo7zorkOoacPY0t1K30rfunNJLJb2mNmawB0VQQEN3GU0NYurTtx06toW1eJb17rOK3K/Lk/S2AMBYUpLe0kUwMIEpEnGvrN86bJxMpIsHZAREI1zkk6y6HJU5ZRc5CQ5gnEXMSHOorOIdVuWpevxQkPrwQOLqAXZmVoO4pW1ItKvrp1nmz2qkUxaemn3Y+tYF1QHotiZ+JFt1BVuxzT2QJCYnS5hxKs2s4naHQnOsY8JDIDs6mdqZzstqBOIi8rAAWEjy9htE8fqiryQsQVLN8cjVpZtgQvTDDXT/rQ+P/Ctm+MQtvQdwLprP1tjp0xza0WsIHVeAh1tywhg5RFTxN5QeihdD10S7VOjES+Gb22tLEDeuoqyBgS6IoClUbZReNWSlTv/OqGxL9Wvro6GrPmQjolkZV0bgmpBNGMPaewjwI7YOgZvvbvEoHYCxW4bcC90EIlYGgEZSRGoJRPbMsEigVW7kBRpQH/bd22KnRaZUhcA7q2/DXB1mwShtPtUouaRbn/Z2+wdQHYGkYTZn6XVJ7c7coTUqJnz7L5Jtk6nSJOBoj12kfEIdsOztlwRArdPLUVgG6McVR9vpcrZckvqnQZYa4/XItEi2qE0PJQo3jbP0kMdGr3Wz6lEy4H16BBjo9lJOdDXMBCM2NfJDHbt1waL/CzufWfkRQdZw6b+2bg4IWNbcgQUMqXYWm+XAaVm7H31BSUzJGNbLK1HpG+zo+oZny6SbSULVzZ3tHcTC8hjNWvrfbW6UEgPed4bY8t0O91Ws3qAcKgee4R9E1lD77VcNuMOjlY/o0DRY+XOIUFOhtLGncvh+NUMqvvIGKQrga7djUVlFdEComXziRdRGbjPV63BjJwQKUuqGyJqSS5SGojsonZQ1rvEBWQb5fEX7YrIYFpJDrJGySAHBGrvSIocCBxHplCwOwXTSEaRjMG71mJFjFwN3cboAAzkB2mZYciOpv5DXWCYVdSSZt++JY2A8yAr82AbS5aoTvuw78Q5GhnBZE6NYGQWCdVWC4ekHK0PmR5BMxEo2kVOTGHKnOxFiEwWlgGlB2aQjSQjkGRr7g9dRB/JDsTiRuC4s/e6v6yMeZ96QbspvTRRQSJiaR0oWlJEBov7OMeXayMZlGMi5QnroLGeU46MkddXB5SasRVzd4x9FNjeYkOtNmdzskkIYHV+q7bDmuLMdTwQ+1ogN8pThwCLLDxPdyuH4wH4BcqYImd3QvJDuBnddmDtdfJEDNi97buDtzRywtLYFXxaN0uwA/BfxHrxN9AKNkfJGFYg6oFNzNoonLL6dBQ74HJYo2Us2REN0jXlh2Z3fSfQparoPZAirguiZQeSJ/KuIeWDOo6Ag9I5KlqGCCByV6XYf3fNno/Jftrv1aX55TZqF5pyHRFL4maTMaYUuUaMbZ/XW12LnXqQXGYQj0+E9SEDsgPVeiCGNhkcSRHFwj6Lr2yM2+0SYxvkGzF09167IlqWSCbXRVBo2oX9eXmkvLW0QMxbX2t58Wh7E+pFDx7Y5lEpgVedkyJ64vdo6NbgsJ0GkFG5aQBma3ABtOYG5IcZLBKeYw9JEfaSMcjhkM7INn1ZL0Xa6j4CGcWU/FCWIQI5KW39AOvCckRNp6H1NqSv+2PhXCHRnCGsLT8f2AeTLEm2TksUB8ya8dG81NDBMIJLy/mwPHAroGSwPgwZtR/61n2XDkyoJoRBJpIt9wPJH+SO6FE6loyp5adKVqDPLJYjAkor2v+3cEMiCXz6vCInjI6J5quGwDNS59EzgVpp2F4XKIHR6AykR1eiCQLCjDyRtpn2t4uRaCFVwUfI/dDMrGRJw8wy0dI5JQuzrvbTUkM+I0aXyRjZrmVn6hi7Sg1VMMVAjsy7IokZVYemAEZgzs4JYlR6ad1No/JDnQ/KigfQ1xdLdzwAMQF2ltlCUoDuCpdEkVOnw5WuJqWZoZZG8qPT05vWRdJCAlfXd3ggJzUIt0283KZQWyomArnxdGCPjHrRMsVzRLKZRPaAbzG9Ub1nMbKWHuQU0bvbNDtDa8/YZgHZYHQT5KjwqfOar70FaFl7lu5GIJfgltuAHGnACyy9PLBnNHY6i+i8z2wH9pwlW8JsYjbjiJJCSr7A4iiz3dJ1LDKsPrfuWmfnQLGTBH2n14GLA7Oh3rMa6aI9/mF9zP3SgocXIngGY3tp9hGW9lyQ0KtOsLHbBsgQax+SII9tTGRkI1Hm0WqH6qpdxpaFTcAVISRBtoEXFzYeqGY6o7HpPjMVkiYEpAaqDUG12M+RIsb0C2aFXzACIqz7yGYXHXliamlLohjTmnVsp0eXi6pDr8pP6+rFCARJyYsiakIWoI9DkEuAiglzmuASyQydpQQDA3b5oW08EH91ckQHlg54n6qxR4udkPaOhn2Fz4lqPjImryFjfCMKHiGDG0VBTf2Kxc4qUCSj1tljaHM/ArDhilB1PuRxluPRsbsDcsTQEvTdmEXuxzEqbU7wuKMam+x1YiLdbEoKR05EsmPmufOrNesCTU1qTCIBudGM1jE6AKHPRYGoHseoNbUx9pKMVDoBT7xYqerMb2ncbbs6EY0bHRcYbU3JW+MVrwLwtOq+gYkkvYKliKXF6JjbK13ZZ2UcCfT4bjSNI1EIeN2kGJpRuSfKTuqkhZYUSJ4ANnZdEIex92Mke9dhZKAISq4DU+TnAXbuWNxzRXQ2EXjayA2xip2mpUh6BtV0qWrA0oZ9OKqho2kUUIcgq1M0oG/9Z7d8FQwogLagJU+MOfIsr3v3pQPrr5MfEphyCgRLksiZrVAqHMkTrbnBnZJBQsYEMGgzrrEH2TuVbAlKUd36EMaLjHrlqpp9CYCWjemBJZjRKBB3csURYINzdcB1QL7VTfOy3Uoks0OW1h1Bb7P0swBrMWqvL6o2iFVQ2DJza4V6tddWADmnsQ/KkjB7aLC3dUw0waS36kA3OMGackHMOYK8bNKdR3jWsJ26A5AeyKs1tJoxigyfmvqZp7q5/zyNj9q2sYOhia07HPaue30toThaknparQjnVgaD9dGWK+LID2uxI8TM3vAjODBYAlCDVQy5gvYeyAzKC1u8YVGGPw21d6CxTcbWurq1KRgNwOWIlZUUIU9rq4q8OkoGuiKgPHVvi5wRi7HDgQZHpUhUy5Gx8sheeNQdu6hlgrTayJgDm8GCmBysUqVZLLADm+O4XyPdAnejhRNShFTCpf9bWFuL8LUlT3QqHBUySRBKCQS8aXNRJJVbcCVHeQzcPRfYCVYmZxBBJFWKzPZYQOb86gRtGyYUlHavlZ0WAtkBtjWELDMZOvStJeNq4O+vl2Yq4yXxujJqiql1oKgTNATm2LMCx23bBbkliJk5q7EDuy9MxiQGDGSGhlmTSKKJ2i3NjSekbKc3IyRVNHBZrUcD7gYusHUx092xXEJgI3ADhmU1nUInS2ScJxwQeD7pdHgFTVIyqNEypAGuOwEKHG02L7ufKkFrZCaj4PHRfjKlHjomEXtzvPxGBOiszPCOt+xBxOhoLKQGadnDfzC4V976tFwyJnXv7kQq6VO2oIzRmEMrNpEARUEjCnazwV1zLif2e7Rb6OjjjFqR9JQLwJt2B+wagCZTexsyA1xMyN4yy8VgrXOjhNVkcWubs++iRs10jOy9JyaLpRs9rqWLETteFNjZYmRpASo9TsiTRnLEGgqWfD5cK5JJurhAtiw+Q5KY2xx2YuB4ELKmAMB0gKnT0MMgHgS253zY75fmPakJdBb1W6NBtybYRXsCEkWDvnE3OuAuEOhQpgC5QuTPic3PZOxMJpENiy8GNJMF9O7WDJgatSUjeHRdksz7DHCTwPbPwRQxcKO3NYMrEF80aIHW7jqJansRt1S+GlOaxTrbTZs/B9hZAAe62tTmweypEaAtj9uTJUiKNMdYNSMeQE9ga0J2n3B42AgeOyvwcS1KM+5Lg1UyLgKylB3at9ZSZWlFebvPTqsTkisGUz9tlHp6RHp68hx73j4yUuwmoKmfqgyN5kCLNZFyRYj6CXTcFbB0FZ8e/oSq85xRJqyGmDFI4Xd3LPU7swS5vg66olBLNBlY6u+4brx6VXsd7OzA06v+e3rwmEmbe5V9og7XBTH1y0C7Ohzo54zGRoBgi+UzsgMkZjx/Os/iS9vJhPwgJDl8iUKEkjGOfmbk0lRm1pV5jZxZGA3O1Vbe4ujvQIqU06RItAhSK1PY9bzJ0dgUALoYo2HIYV+P4dAcIjNShL20PMj6hVJkTYsLwKKUOgFJgbxvL5Bs7qCWFLEA3FqO2OUAE+IUnaAZBzY/FdgawDDtnfG8La+Z8LLRnUdtMTay+yxHRN8pQPshfT0TXCov/qLS25b7safntfetnTXkgFjBo2TwTB11Xd1LsrXsAOr6OtOZFW4XDXtW8JiceHJIVxtrnU8COmJsk6Wjwic0+sVzUrIOi+lStMGhWSNiBY/AISHPtlOs3HnRlhTRPjZyOmwZcsvIOsDmg64I57JIIyWugxlG83XA6pSQFmYgaYEfBWKRxIhckBRDi3JOw7cmpVfZyEp2eluDGYEWnV8C0xjZgkePM5mjYkThqrMvK0UMYKOMndLL0iAvRhsa2NfVdJC9QGlKilgZTQvMEfiRk2IkdthKowNnI2ynHI+unRpLifZrMMPtnhuCisBQul0f37D40lQNWkP2UvvkABFjzpPut+ykyMEJKVP7skyeYO4OoIPyY5ixrQDSGvyalSSKpcmyGQ29DNnWYmGkves2JUtI62ggKbIsHmhpd7XdLGu/LbATtSSHNLZTDBXKD9QhLOmAmBeAPwgUqVb5Idlh1W645wdSIx0wgkrHJkkC2vcOyAPERQaMBlA98PJA6vzdgN2kyiNXJAouPYADTz3D2JCNwTaykimWbo6YWw6JyjolViCoLD7ieEUGqL21hWcBWmceXY2tMo3bYa+vrwwSYxGbvxuwM2n0IR/bqwx0wKovphVcstcGgMyrFuxYHXYEJmJ76Y8MG3tgdz1oA8wMxlmagEYgtnQ1ki0itdzUVzt11u8L7MzgAiN4zEy5QEZJK6yLRkB1zpsCuIyHB9i5qUE2JsCcqhC0AI22WUkWkKzxLECK7D6UgFHncIELTAokScaAPTJTqiE3UovmuAVPY0xt1WhDbxt1JMf/NjoGd4OIHb+7KRsAUoY9eQMAz+h4Vm4WCIbdWhHktJAxe5Pp4gg3hwZmarIeaFbZU2pFkjOtwuFihr7mDJiTYEdSxNXdhl9NTq2IKWWyOtsIClO+t7GtZIM/Xail/WpSYxAt/YwSNDoVbuljzdCoTFUztDMM7O2kiKezg/GRBUy+WSzZAbfdSTADcKSRIUgQcL30eWTZHQTxcHreygQikKrxmB2gaw21BWjF3M0AAgR4ANDsOEYr+dK1KwDdo8AO16Ax9Lc1oaXLypEUIWPWJ2N0DmqrwcfACnRZu03+PgXE5nqTVjmt1s/I+qN2GBdsiwDdFDEtNpvr4BEkgjjQ04i54XH8DMaOhpFF9c+jYx51Jd/jfzbEwKZHHrkn+4UDU595DHsUxA4QXWtO1ZPsulwXNmm7j+yJh/Y1GskecY50OQcyg5NS43nBo1FnHQWb2WkZ0vLFYvO2aIvNJfcsj9xyT/aLwYSSIFZAac1V4jop4Bh3lLrZAUGUZ1xnPZgATW22nTOHkdGA8KzAMcXYSDcHnSGc59oALJxgkvyp0ayhYebElJbeRp56c25nSoMobT5SNOWxeCQfsjIjk0EEFl57/s0FQRLDCC4pESB6Wjpi+mFgh84IO6uEDfjboSxxspjFCSTNANMFfm7GqDigTNiDAdtzoJc7aYHa6ZJS1AlQZtHyovXxyUAQ+tWGi1IGg8gRYBepXWd0drgMB7Ur5XptkayBLBsBEn1/FAg6mUcT6MFxBdmRGSBrvbxKrCUqrHpc2xRj6+2d/l7gtUOjYdB1zrByNNnkWcBOOyPW3Ndonj8EYssutOa8dpM5CfZuvxebssRj2C7FbmUho+3GiHrOtFsF72KwLfKVLcZ2qvPKtmgUzB57WUU1vhSNSkfnIYO5x4GdnIRytk2UzCFD73IAfDj/tSdD9I8spofr9kfTE+uLZU2fhtpRX/tOVrt15wICQRRcep+HQCZfW/utgA7VUb9lcCh+XjqLsVMzsDpzjVhrM2YkSHpFAyhPuFuuDy2nFxZBAUAqNr2XpmZ0d4a1LQZH+lhrYsu+A7UehqYuTeESuCt02tiYLRUureHMge1ZfTW3OyVFFBDhpJUdkJP7KCFLUJCX0uNqwh1zLj9HKzPoPBYgzWU7PC2fCBbtNncj2dXjugMgIHdyA8sSvbKwm2TJTEnmFTw5qfTo+KcydpRWR72cyBlS5uwnVLKqrTkkR9At3EniWOWqPFveGmnpaPvAfraAfGfnprir7RCLu4Z99/tYLO0B3QN4MjkjXrekn9DYhbxS08AJSc8UFbG3ux2MnHeki6dFydPQVnpea2pq03hW0JX5vHCdR6sz1tKPLe9dkHxCZDczA9OIdp7R2bl1HnmcsQdZOUrylGA0jcXeRScHyFmZ17/gZgFWVk9HrJzxujt3R06G43QojvY/fjsm4ITA9g3jMkE2Nti708eogs/T2QNyhRKsfgjYUYlqCvhWwNmcW4CY7KWl2dDZWQCzlQRy7Lq9Go79tSRdne1II7aOt47JAJjsiR+bpUwSYPbAGI58Qc6Lce53A3YIfENXY4nA7jrr5oUG4DY1eAbkqEYCMfGSBLEjk8xthsPham7HdSrGZD9sOFFu8sTS2KLD77cMqwY7p5178Aagz/vYB4E9NbOUB36LRZwEznAbr+M47cNtlvPiuDFQYmX3GaBqj1849buO6ONjc6W+TRFUGtimHOmXW7FWMggn2/GsvwSLD7EyYHxrbck0C4+yNjtr3UyyscvOERMHjggNuCIlsPfeR4p0bgATJ2tJLMC5Qac3mQ7ynL2O4IFcanYAOJdxR4CtfyNHdhRn7u80mB09TU6yxdXGlsZ27hJmLUiQ7XwusDWABxgclr4m2SQEpeV9nwByL0B1QdsWVrFcszIF+oS0cbW09f97/FdszzkjRZJyhS1plNXXRl35uMaOxFFmrhD1xUb1udcZjIvFkdQpE+C2sm1eMJpmUE8rO/83GgEx/ty9ihECbeb7zurgo8eHGpsXDiv5RgNEj7WT9d2uo2ItxzEK2iTYyUnLp6v92u/dlATLOg1znvBB7dw/+0EigaFcpguSTINzkq3T+johU6akSHaJDsjagdSIFjs1s4fO+TMyxgoQIZNlA8r4eUkHijPvO53L8e8gvG0v6cWg4tDS36E00RZeUKqaeT9u92V85ZHEjiM1QpAbtSYzdmHEjFF14nEmdTrRyHu0bAkCdUYWuBKk/Z3Ndt+N3YcA6Q02IDxVgwvepN3nZT6jklZOHGNO0zDyHCSV0s9aoliM7ZUfoDtlYrQLlCBBytySKFa6nGxWpyhwPE+KDMiRMKCM0vAJSRI5HpRlStlXbfa7ZdBPA77TISLgRisbQ1BnXI1gon6KRrokpUemHJWMKUOeI0UiAEdTMYwGoFEncOrA3Yvu3QFsVl8gqM6QIQ77UVbCNMcarkfW1bBG1Jz9OH9UTZKxR4HuJnGIOGDq6PaWAasbaEaMHQ0yMH6j9DFeDBAlo9Axe7DHYW6Aoo7kZQkz1ysafpYIDjNs7LR5QAytGmYOzHVsQE9SpMG97czKk+KAKp3sQY7HLNAzy47MtKW6biLq2Oxeg0wqPEMOoezIANnyzLPBq3e8/jGml5weqSPJShLOuyjDFqHD5vjYx/cJGbUCb1Lbpx2LrKsxW0wVnY++o8f0Aqbgl23uCY7WnpUnU+7JCMPPyowDTJzd1v+/OBWDQFYeAf8RhvZkx4RfnQ4cTwV2NEtrJqiU7cpjje60Jn8AneqkiaNMRhkQe3cp5O86QB0Gu1G4RGC125LVx2jbetLriZp5sLDpHGBPShHLwjvC2g+rK8hsBuvcVLme8s2zQI+2efp9NJBrti1THfKQvLgabkVWF3tuR/TZZ0if86RIctL3DLgza9dIZrYmqEH1IwGLn3LL9lh7qKPheVBGO2SKvYPEC5FThjoSJCKmTciS5zA24XFooRyJJEiWxTNzAaokQpQkQpLnLKAfPSeB5AodYWyLAVUHJBqo2JsNLmfYODdKfYKxA8CH1mDSCvQKqSxWBuf39bUJpP6zonPY+npEM2P9nMnOlpH/HwgiM+egTEdR1zBt6SXS66MMPszYYHuh7LwUA4GkWW/iHecx/9FE0Oj5ZkGIZq0a7ZyoDmQw8Btm5yNa+t3tvpEgMqG1R7S3aw96LHPkdTLtn2ZytyP6CZamrTMV3bD9lvndRkE9auENdJIzGbvFa8kHkSnNPiBJZgLNDHDdi5w4b+qc3SxRTJz9bkmdfMb/N2TcqKYjkzn8sIxN9thFo92OwUh7Rzo6vHAJPV4GgdBctPKoQ7bYGUwhRpnpJbyObcYng4w99LskXQ6igXR4Evg8KGfO0dieHMGA56jNCFOHgWhGj88Cf5kBSK+bKWGnzciL8PhZ3TzKxLMDD7JVfoVyc5aMMvYRxyTldQdMHTokVjDoXNBhbWkyNZPXbjTYTcus5P+LPKdkhomNyTh5EugpHc1HGDuQHOEqYhG4FXLDYHNUk0ermM12ElcK+exMdJJMGOzU0y7FjGaekSSznnd0HsjYM6zt6XJyRronLpJnBWZ04ogW5DRgOHdbH0lKTcgn+LsIJh7pDFbsEjK1NY1yhr0D9vVUB4dSZBCogzo7Ykq4UkLWCoykzIiV6DHxoSB1FEwj54kst0TChJ7hdhhsTUfvJIdckQjYFM/slJMkdF9jbSTAnGD39EUHGplpXn+OWKBDccSBzhp9f5eFI2khpmXoOsuSKKoaBPv5jD2RxBk5Dx6x028cuYB1g3Q3pHNxNFB96/dHp2oY6/BZC4/e9yHZ83RgT7B59hyjXni3jZNgPgbAfST7mwJ+BuRngnrGyjtbgvAJUmTKObFkg9HhzbYZptbgHQTDDKM1/43RGveJ+GI0wKbJ/2d4nLXdq8o7wb15jhSZ9bsHrcFsoJoB86yGPxVUM4BCi5jOaOAjID8jufKWD5Oxk9LBZW1w8VOMjgB6hNEHEwxHbs9hJ06SSGv9Dciu9B1tipHLYUaOnJgZv9wEthqIOxoIuh3A9bfxx3qMDgGe1ONZ5h0CQ7ZjDTLlcCcdZd5BLb2dM10EN8XgZ2ruO2MfdDhGJos/IdAsB9j7CCCHZIkHSmpN/BlpcZB5c21naq3z2jlb9XEA2PX/1S3Cl7fuPPBOe+KelDF+laKX4R3sPEdAnwXaoeNrleGIlJpxNwInYzggjGK/sx2SZuJ3PmDRhaxN7pjJCMQm87rMSJRmrUmgjDBZulN7bXngt7G265R74ndUv03LK0ndTHQg4TLaAf52xN04W49nLURA12WyUwwBYoThs9uzDFwGOqIV1M2yrTeV2DlTKZwvS04DNg0PQvBkjdkAsdYRhya8G6hfvDy+4jIN5sZZSLbnHrSH70RHPeWz5gep671/VGCnwX00+TMhW47q+SkpdNb2JNvOMvHwOc/UxM8aQub52MM6Owku72KOtPH2W6CYBcbsxR+3QOc6bXnj3ymjpynB5jQC6pFOEDB2s7LV6MPoEJ2eOpoIOhqcpi/+IDBm2HgYcINgmw7uzkqcPJOlB4DNIyycBCQfYvkzAH7UofkI7DgA1jMAfRr7zoB6ht1DjX1Ab89ImRR7fwCpc5R1h/d/VKnw7OnNnhY8ngDspwSgA3eRMzpCBMK3API0mMeBWp7Gvm/1+Nsg8ArPoXtUyqCMm+V0Ztj57HanAz3bZhLMg+2Yjp7zqJQ42nlGgW2AO22wz2j1e7bsCSw+AvKzgX4AyKeAeVIbz7gYU4A+ekcYBjae6myYxGeYf6RTZIE7At5poI+A/RiQywiYnwbojyBTMj72Wcx7BFAzoBllLXoyez29E6shacO/x0jny/+O4+nyo0w/K0XO0NxHWfasTjLTUUaY9gigZjrlrFSgGSDl2H8K1IeZ/iiwz2LvM0F+FOizYG+0AJ94VzkDxGcAeTZ4PJulM/eAM4BNZ53D+PJHQT7LsNOMy+eC9wwmPgTEZ4F5GmuJNhf6oA+mv9qj0Ofj7X4rwdiHa2LPYNZnSYQzde8kGy+ZyQ3PYGXjPLnre4bkOX4n4DOBzU8B4BNB/iywHwnc5jrR3PkHwcbvCuK3ljWnaewPAvJngfIwsM7sCCd+5pvoo/fQ6G8B7Cez65SEKk8E5FNBdLZEeiaIZyTW9wrsJ7Arv+v3+/46yLFYaqhc4ZRP/H6BffqF5I/5H/ogtggf/Z3KaFd5j4tx+bz+/18f5Qld5eP8Xz4gYx917/hD9o6Pdxd57u/0tvKDv0sp8l1xx1vfisoH/V/zO/8PLx8bqOU9MfPZlT/ENZ77H94Y+4cff/iUnJ+Pv9Tj/wQYAFpG1619RA5UAAAAAElFTkSuQmCC');
  background-repeat: no-repeat;
  background-color: red;
  width: 182px;
  height: 182px;
  margin: 7px;
  float: left;
  cursor: pointer;
  _margin: 7px 7px 7px 4px;
  _cursor: hand;
  _background-image: none;
  _filter: progid :   DXImageTransform.Microsoft.AlphaImageLoader (   src
    =
     'mask.png', sizingMethod =   'scale' );
}

.x-cp-rgbslider {
  position: relative;
  left: -7px;
  top: -7px;
  width: 15px;
  height: 15px;
  background-image: url('data:image/gif;base64,R0lGODlhDwAPAIcAAG+U0myi55e36aC63ZTJ/53M863K6a7L6ajL/6rM/6vN/67P/6Xf/6re/6zf/67f/7HL67LN67bR7rDQ/7PS/7TT/7XT/7XU/7jW/7nX/7rX/7vZ/7zZ/77a/7/b/6fg/6jh/6zj/6/h/63k/7Dn/7Pm/7Ho/7Lo/7Lp/7br/7fs/7ju/7nu/7vw/7zx/73x/7/y/8Db/8Hc/8Pd/8Te/8Xf/8fg/8fh/8jh/8rj/8vj/8vk/87l/8/m/8Hz/8H0/8L1/8T2/8T3/8X3/8f6/8n6/8n7/8v8/8z9/83+/87+/8///9Dn/9Hn/9Lo/9Tq/9Xq/9bq/9js/9rt/9vu/9H//9P//9T//9X//9f//93w/93x/97w/9/y/9j//9r//9z//93//97//9///+Dy/+Hz/+P0/+T1/+X2/+b2/+f3/+D//+H//+L//+P//+T//+b//+f//+j3/+n4/+r5/+v6/+j//+n//+r//+v//+37/+77//D///L//////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAH4ALAAAAAAPAA8AAAhdAP1AEECwoEEBEvwYENCnocOHfRAy9EORIoCKFCNOxHgRo8Y+GP10rPgxJEiPBE+GRMkQgEuVfVwCKLmSpcqMJlOGHJlRJ8ecGyvy9BNxAEOIEAVE8GP04MEDfgICADs=') !important;
  background-repeat: no-repeat !important;
  cursor: pointer;
  _cursor: hand;
}

.x-cp-huepicker {
  height: 183px;
  width: 9px;
  float: left;
  margin: 7px 0 0 7px;
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAC3CAMAAAD3j4QnAAAAB3RJTUUH2AQdEAg7AL7dPAAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAIKUExURYiIiPYAEvYDEvYSEvYcEvYlEvYtEvY2Evc/EvdHEvdQEvdZE/diE/drE/d1E/h+E/iHFPiSFPmbFPmmFPmwFfm5FfrEFfrOFvrZFvvkFvvuF/z6F/n/F+//F+X/Ftv/FdL/Fcj/FL7/FLX/E6z/E6P/Epr/EpL/EYn/EYH/EXn/EHH/EGr/EGP/EFz/D1X/D0//D0n/DkP/Dj7/Djn/Djb/DjL/DjD/Di7/Diz/Div/Dyv/Eiv/Fiv/Giv/ICz/Jiz/LCz/Miz/Oiz/QSz/SC3/UC3/WC3/YC3/aC7/cC7/ei//gi//izD/lDD/njH/qDH/sTL/uzP/xTP/zzT/2TX/4zX/7jb/+Tb8/jTx/jPm/jLb/jDR/S/G/S28/Syx/Sun/Sqd/SmT/SiJ/SeA/SZ2/SVt/SRk/SNa/SJS/SJJ/SE//SA3/SAu/SAl/R8c/R8R/R8D/R4A/R8A/SEA/SMA/ScA/SsA/TAA/TUA/ToA/UEA/UcA/U4A/VUA/V0A/WQA/WwA/XQA/XwA/YQA/Y0A/ZYA/Z8A/agA/rEA/rsA/sQA/s4A/tgA/uIA/uwA/vYA/vkA+PkA7PkA4fgA1/gAzfgAxPgAufgAr/cApvcAnPcAk/cAivcAgfcAePcAb/cAZ/YAXvYAV/YAT/YAR/YAQPYAOfYAM/YALPYAJvYAIfYAHPYAGPYAFcyqodcAAAHBSURBVHjajdXnVggAAEDhUmgpkQgNGSUjkorSQkZoUNlklWySSJmpqKyEiMgo6h2759zT6fSL79d9gxsQMCVQ1LioMVF/Rf0RNSpqRNRvUb9E/RT1Q9SwqO+ivokaEvVV1BdRg6I+i/okakDUR1EfRL0X1S/qnag+UW9FvRH1WtQrUS9F9YrqEdUt6oWo56K6RHWK6hD1TFS7qKeinoh6LOqRqIeiHohqE9Uq6r6oFlH3RN0V1SzqjqgmUbdFNYq6Jeqm/lk3RF0XdU3UVVFXRF0WdUlUg6iLoupF1Ym6IOq8qHOizoo6I6pW1GlRp0SdFHVC1HFRx0QdFXVE1GFRNaKqRVWJOiTqoKhKURWiykWViTogar+ofaJKRe0VtUfUblG7RJWI2ilqh6jtoopFFYkqFFUgKl/UNlF5onJFbRW1RVSOqGxRWaI2i8oUtUlUhqiNojaIShe1XtQ6UWtFrRGVJmq1qFRRKaJWiVopaoWo5aKSRS0TlSQqUVSCqHhRS0UtEbVYVJyoRaIWiooVtUBUjKj5ouaJihY1V1SUqEhRc0RFiAoXFSYqVFSIqNmiZomaKSpYVJCoGZr2t/+tSRPCSaUaByq0qgAAAABJRU5ErkJggg==') !important;
  background-repeat: no-repeat;
  cursor: pointer;
  _cursor: hand;
}

.x-cp-hueslider {
  position: relative;
  left: -3px;
  top: -7px;
  width: 15px;
  height: 15px;
  background-image: url('data:image/gif;base64,R0lGODlhDwAPAIcAAG+U0myi55e36aC63ZTJ/53M863K6a7L6ajL/6rM/6vN/67P/6Xf/6re/6zf/67f/7HL67LN67bR7rDQ/7PS/7TT/7XT/7XU/7jW/7nX/7rX/7vZ/7zZ/77a/7/b/6fg/6jh/6zj/6/h/63k/7Dn/7Pm/7Ho/7Lo/7Lp/7br/7fs/7ju/7nu/7vw/7zx/73x/7/y/8Db/8Hc/8Pd/8Te/8Xf/8fg/8fh/8jh/8rj/8vj/8vk/87l/8/m/8Hz/8H0/8L1/8T2/8T3/8X3/8f6/8n6/8n7/8v8/8z9/83+/87+/8///9Dn/9Hn/9Lo/9Tq/9Xq/9bq/9js/9rt/9vu/9H//9P//9T//9X//9f//93w/93x/97w/9/y/9j//9r//9z//93//97//9///+Dy/+Hz/+P0/+T1/+X2/+b2/+f3/+D//+H//+L//+P//+T//+b//+f//+j3/+n4/+r5/+v6/+j//+n//+r//+v//+37/+77//D///L//////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAH4ALAAAAAAPAA8AAAhdAP1AEECwoEEBEvwYENCnocOHfRAy9EORIoCKFCNOxHgRo8Y+GP10rPgxJEiPBE+GRMkQgEuVfVwCKLmSpcqMJlOGHJlRJ8ecGyvy9BNxAEOIEAVE8GP04MEDfgICADs=') !important;
  background-repeat: no-repeat;
  cursor: pointer;
  _cursor: hand;
}

.x-cp-formcontainer {
  float: left;
  width: 116px;
  padding: 2px;
  margin: 7px !important;
}

.x-cp-clearfloat {
  clear: both;
}

.x-cp-colorbox {
  margin: 2px 5px 0 5px;
  border: 1px solid black;
  text-align: center;
  font-size: 10px;
  height: 20px;
  font-weight: bold;
  padding: 3px 0;
  cursor: pointer;
  _cursor: hand;
}

.x-cp-formcontainer input {
  text-align: center;
}

.x-cp-leftarrow {
  background-image: url('data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5Ojf/2wBDAQoKCg0MDRoPDxo3JR8lNzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzf/wAARCAAJAAkDASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAAAAUH/8QAIRAAAAQFBQAAAAAAAAAAAAAAABESEwIFBhQVITFBQoH/xAAUAQEAAAAAAAAAAAAAAAAAAAAC/8QAGBEAAwEBAAAAAAAAAAAAAAAAAQIRADH/2gAMAwEAAhEDEQA/ANSqDLZSV2a7F+B5k1GrVRdS83PgXwAJmoAnMVWEm93/2Q==') !important;
  background-repeat: no-repeat;
  background-position: center center;
  padding: 0 2px 0 2px;
  width: 9px;
  height: 25px;
}
</style>
<script type="text/javascript">
// Color picker from https://github.com/osnoek/Ext.ux.ColorPicker with following changes:
// - images as data links in css style
// - background color of field set onSelect
/**
 * @class Ext.ux.AdvancedColorPicker
 * @extends Ext.BoxComponent This is a color picker.
 * @license: LGPLv3
 * @author: Olav Snoek (extjs id: osnoekie)
 * @constructor Creates a new ColorPicker
 * @param {Object}
 *            config Configuration options
 * @version 1.0.0
 *
 */

Ext.define('Ext.ux.colorpicker.ColorPicker', {
  extend : 'Ext.container.Container',
  alias : 'widget.ux.colorpicker',
  width : 350,
  config : {
    hsv : {
      h : 0,
      s : 0,
      v : 0
    }
  },
  items : [ {
    xtype : 'container',
    itemId : 'cRgb',
    cls : 'x-cp-rgbpicker',
    items : [ {
      xtype : 'container',
      itemId : 'rgbPicker',
      cls : 'x-cp-rgbslider',
      width : 15,
      height : 15
    } ]
  }, {
    xtype : 'container',
    itemId : 'cHue',
    cls : 'x-cp-huepicker',
    items : [ {
      xtype : 'container',
      itemId : 'huePicker',
      cls : 'x-cp-hueslider',
      width : 15,
      height : 15
    } ]
  }, {
    xtype : 'form',
    itemId : 'cForm',
    border : false,
    cls : 'x-cp-formcontainer',
    items : [ {
      layout : 'column',
      border : false,
      items : [ {
        layout : 'anchor',
        border : false,
        defaultType : 'numberfield',
        defaults : {
          anchor : '99%',
          labelWidth : 10,
          value : 0,
          minValue : 0,
          maxValue : 255,
          labelSeparator : '',
          hideTrigger : true
        },
        columnWidth : .5,
        items : [ {
          fieldLabel : 'R',
          itemId : 'iRed'
        }, {
          fieldLabel : 'G',
          itemId : 'iGreen'
        }, {
          fieldLabel : 'B',
          itemId : 'iBlue'
        } ]
      }, {
        layout : 'anchor',
        border : false,
        defaultType : 'numberfield',
        defaults : {
          anchor : '99%',
          labelWidth : 10,
          value : 0,
          minValue : 0,
          maxValue : 255,
          labelSeparator : '',
          hideTrigger : true
        },
        columnWidth : .5,
        items : [ {
          fieldLabel : 'H',
          itemId : 'iHue',
          maxValue : 360
        }, {
          fieldLabel : 'S',
          itemId : 'iSat'
        }, {
          fieldLabel : 'V',
          itemId : 'iVal'
        } ]
      } ]
    }, {
      layout : 'anchor',
      border : false,
      defaults : {
        anchor : '99%',
        labelWidth : 10,
        labelSeparator : ''
      },
      items : [ {
        xtype : 'textfield',
        fieldLabel : '#',
        itemId : 'iHexa'
      } ]
    }, {
      defaultType : 'container',
      border : false,
      items : [ {
        layout : {
          type : 'hbox',
          align : 'top'
        },
        defaultType : 'container',
        items : [ {
          width : 30,
          height : 25,
          itemId : 'cWebsafe'
        }, {
          cls : 'x-cp-leftarrow'
        }, {
          xtype : 'button',
          text : 'Websafe',
          itemId : 'bWebsafe',
          flex : 1
        } ]
      }, {
        layout : {
          type : 'hbox',
          align : 'middle'
        },
        defaultType : 'container',
        items : [ {
          width : 30,
          height : 25,
          itemId : 'cInverse'
        }, {
          cls : 'x-cp-leftarrow'
        }, {
          xtype : 'button',
          text : 'Inverse',
          itemId : 'bInverse',
          flex : 1
        } ]
      }, {
        layout : {
          type : 'hbox',
          align : 'middle'
        },
        defaultType : 'container',
        items : [ {
          width : 30,
          height : 25,
          itemId : 'cSelect'
        }, {
          cls : 'x-cp-leftarrow'
        }, {
          xtype : 'button',
          text : 'Select Color',
          itemId : 'bSelect',
          flex : 1
        } ]
      } ]
    } ]
  } ],

  constructor : function(config) {
    var me = this;
    me.initConfig(config);
    me.addEvents('select');
    me.callParent(arguments);
    return this;
  },

  afterRender : function(component) {
    var me = this;
    me.callParent(arguments);
    if (me.value)
      me.setColor(me.value);
  },

  initEvents : function() {
    var me = this;
    me.callParent();

    me.down('#cRgb').getEl().on('mousedown', me.rgbClick, me);
    me.down('#cHue').getEl().on('mousedown', me.hueClick, me);

    me.down('#iHexa').on('blur', me.hexaChange, me);
    me.down('#iRed').on('blur', me.rgbChange, me);
    me.down('#iGreen').on('blur', me.rgbChange, me);
    me.down('#iBlue').on('blur', me.rgbChange, me);

    me.down('#iHue').on('blur', me.hsvChange, me);
    me.down('#iSat').on('blur', me.hsvChange, me);
    me.down('#iVal').on('blur', me.hsvChange, me);

    me.down('#bWebsafe').on('click', me.websafeClick, me);
    me.down('#bInverse').on('click', me.inverseClick, me);
    me.down('#bSelect').on('click', me.selectClick, me);
  },

  websafeClick : function() {
    var me = this, rgb = me.websafe(this.getColor());
    me.updateMode = 'click';
    me.setColor(me.rgbToHex(rgb));
  },

  inverseClick : function() {
    var me = this, rgb = me.invert(this.getColor());
    me.updateMode = 'click';
    me.setColor(me.rgbToHex(rgb));
  },
  selectClick : function() {
    var me = this, color;
    color = me.down('#cSelect').getEl().getColor('backgroundColor', '', '');
    this.fireEvent('select', this, color.toUpperCase());
  },

  getColor : function() {
    var me = this, hsv = me.getHsv();
    return me.hsvToRgb(hsv.h, hsv.s, hsv.v);
  },

  setValue : function(v) {
    this.value = v;
    this.setColor(v);
  },

  setColor : function(c) {
    var me = this;
    if (me.rendered) {
      c = c.replace('#', '');
      if (!/^[0-9a-fA-F]{6}$/.test(c))
        return;
      me.down('#iHexa').setValue(c);
      me.hexaChange();
    }
  },

  selectColor : function(event, element) {
    this.fireEvent('select', this, Ext.get(element).getColor('backgroundColor', '', ''));
  },

  rgbChange : function(input) {
    var me = this, temp = me.rgbToHsv(me.down('#iRed').getValue(), me.down('#iGreen').getValue(), me.down('#iBlue').getValue());

    me.updateMode = 'rgb';
    me.setHsv({
      h : temp[0],
      s : temp[1],
      v : temp[2]
    });
    me.updateColor();
  },

  hsvChange : function(input) {
    var me = this;
    me.updateMode = 'hsv';
    me.setHsv({
      h : me.down('#iHue').getValue(),
      s : me.down('#iSat').getValue() / 100,
      v : me.down('#iVal').getValue() / 100
    });
    me.updateColor();
  },

  hexaChange : function(input) {
    var me = this, temp = me.rgbToHsv(me.hexToRgb(me.down('#iHexa').getValue()));
    me.updateMode = 'hexa';
    me.setHsv({
      h : temp[0],
      s : temp[1],
      v : temp[2]
    });
    me.updateColor();
  },

  hueClick : function(event, el) {
    var me = this;
    me.updateMode = 'click';
    me.moveHuePicker(event.getXY()[1] - me.down('#cHue').getEl().getTop());
  },

  rgbClick : function(event, el) {
    var me = this, cRgb = me.down('#cRgb').getEl();
    me.updateMode = 'click';
    me.moveRgbPicker(event.getXY()[0] - cRgb.getLeft(), event.getXY()[1] - cRgb.getTop());
  },

  moveHuePicker : function(y) {
    var me = this, hsv = me.getHsv(), hp = me.down('#huePicker').getEl();
    hsv.h = Math.round(360 / 181 * (181 - y));
    hp.moveTo(hp.getLeft(), me.down('#cHue').getEl().getTop() + y - 7, true);
    me.updateRgbPicker(hsv.h);
    me.updateColor();
  },

  updateRgbPicker : function(newValue) {
    var me = this;
    me.updateMode = 'click';
    me.down('#cRgb').getEl().applyStyles({
      'backgroundColor' : '#' + me.rgbToHex(me.hsvToRgb(newValue, 1, 1))
    });
  },

  moveRgbPicker : function(x, y) {
    var me = this, hsv = me.getHsv(), cRgb = me.down('#cRgb').getEl();
    hsv.s = me.getSaturation(x);
    hsv.v = me.getVal(y);
    me.down('#rgbPicker').getEl().moveTo(cRgb.getLeft() + x - 7, cRgb.getTop() + y - 7, true);
    me.updateColor();
  },

  updateColor : function() {
    var me = this, hsv = me.getHsv();
    var rgb = me.hsvToRgb(hsv.h, hsv.s, hsv.v);
    var invert = me.invert(rgb);
    var websafe = me.websafe(rgb);
    var wsInvert = me.invert(websafe);

    if (me.updateMode != 'hexa') {
      me.down('#iHexa').setValue(me.rgbToHex(rgb));
    }
    if (me.updateMode != 'rgb') {
      me.down('#iRed').setValue(rgb[0]);
      me.down('#iGreen').setValue(rgb[1]);
      me.down('#iBlue').setValue(rgb[2]);
    }
    if (me.updateMode != 'hsv') {
      me.down('#iHue').setValue(Math.round(hsv.h));
      me.down('#iSat').setValue(Math.round(hsv.s * 100));
      me.down('#iVal').setValue(Math.round(hsv.v * 100));
    }

    me.setButtonColor('#cWebsafe', websafe);
    me.setButtonColor('#cInverse', invert);
    me.setButtonColor('#cSelect', rgb);

    if (me.updateMode != 'click') {
      var cRgb = me.down('#cRgb').getEl(), cHue = me.down('#cHue').getEl(), hp = me.down('#huePicker').getEl();
      hp.moveTo(hp.getLeft(), cHue.getTop() + me.getHPos(me.down('#iHue').getValue()) - 7, true);
      me.down('#rgbPicker').getEl().moveTo(cRgb.getLeft() + me.getSPos(me.down('#iSat').getValue() / 100) - 7,
          cHue.getTop() + me.getVPos(me.down('#iVal').getValue() / 100) - 7, true);
    }
  },

  setButtonColor : function(id, rgb) {
    var me = this, dq = Ext.DomQuery, invert = me.invert(rgb);
    me.down(id).getEl().applyStyles({
      'background' : '#' + me.rgbToHex(rgb)
    });
  },
  /**
   * Convert X coordinate to Saturation value
   *
   * @private
   * @param {Integer}
   *            x
   * @return {Integer}
   */
  getSaturation : function(x) {
    return x / 181;
  },

  /**
   * Convert Y coordinate to Brightness value
   *
   * @private
   * @param {Integer}
   *            y
   * @return {Integer}
   */
  getVal : function(y) {
    return (181 - y) / 181;
  },

  hsvToRgb : function(h, s, v) {
    if (h instanceof Array) {
      return this.hsvToRgb.call(this, h[0], h[1], h[2]);
    }
    var r, g, b, i, f, p, q, t;
    i = Math.floor((h / 60) % 6);
    f = (h / 60) - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i) {
    case 0:
      r = v, g = t, b = p;
      break;
    case 1:
      r = q, g = v, b = p;
      break;
    case 2:
      r = p, g = v, b = t;
      break;
    case 3:
      r = p, g = q, b = v;
      break;
    case 4:
      r = t, g = p, b = v;
      break;
    case 5:
      r = v, g = p, b = q;
      break;
    }
    return [ this.realToDec(r), this.realToDec(g), this.realToDec(b) ];
  },
  /**
   * Convert a float to decimal
   *
   * @param {Float}
   *            n
   * @return {Integer}
   */
  realToDec : function(n) {
    return Math.min(255, Math.round(n * 256));
  },

  websafe : function(r, g, b) {
    var me = this;
    if (r instanceof Array) {
      return me.websafe.call(me, r[0], r[1], r[2]);
    }
    return [ me.checkSafeNumber(r), me.checkSafeNumber(g), me.checkSafeNumber(b) ];
  },

  checkSafeNumber : function(v) {
    if (!isNaN(v)) {
      v = Math.min(Math.max(0, v), 255);
      var i, next;
      for (i = 0; i < 256; i = i + 51) {
        next = i + 51;
        if (v >= i && v <= next) {
          return (v - i > 25) ? next : i;
        }
      }
    }
    return v;
  },

  invert : function(r, g, b) {
    if (r instanceof Array) {
      return this.invert.call(this, r[0], r[1], r[2]);
    }
    return [ 255 - r, 255 - g, 255 - b ];
  },

  getSPos : function(saturation) {
    return saturation * 181;
  },

  getVPos : function(value) {
    return 181 - (value * 181);
  },

  getHPos : function(hue) {
    return 181 - hue * (181 / 360);
  },

  hexToRgb : function(hex) {
    var r, g, b;
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);

    return [ r, g, b ];
  },

  rgbToHex : function(r, g, b) {
    var me = this;
    if (r instanceof Array)
      return me.rgbToHex.call(me, r[0], r[1], r[2]);

    return me.toHex(r) + me.toHex(g) + me.toHex(b);
  },

  toHex : function(n) {
    n = parseInt(n, 10);
    if (isNaN(n))
      return "00";
    n = Math.max(0, Math.min(n, 255));
    return "0123456789ABCDEF".charAt((n - n % 16) / 16) + "0123456789ABCDEF".charAt(n % 16);
  },

  rgbToHsv : function(r, g, b) {
    if (r instanceof Array)
      return this.rgbToHsv.call(this, r[0], r[1], r[2]);

    r = r / 255, g = g / 255, b = b / 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h, s, v = max;

    var d = max - min;
    s = max == 0 ? 0 : d / max;

    if (max == min) {
      h = 0; // achromatic
    } else {
      switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / d + 2;
        break;
      case b:
        h = (r - g) / d + 4;
        break;
      }
      h /= 6;
    }

    return [ h, s, v ];
  }
});
/**
 * @class Ext.ux.form.ColorPickerField
 * @extends Ext.form.field.Picker This class makes Ext.ux.AdvancedColorPicker
 *          available as a form field.
 * @license: BSD
 * @author: Olav Snoek (extjs id: osnoekie)
 * @constructor Creates a new ColorPickerField
 * @param {Object}
 *            config Configuration options
 * @version 1.0.0
 */

Ext.define('Ext.ux.colorpicker.ColorPickerField', {
  extend : 'Ext.form.field.Picker',
  requires : [ 'Ext.ux.colorpicker.ColorPicker' ],
  alias : 'widget.ux.colorpickerfield',
  matchFieldWidth : false,
  createPicker : function() {
    var me = this;

    var picker =  Ext.create('Ext.ux.colorpicker.ColorPicker', {
      floating : true,
      focusOnShow : true,
      baseCls : Ext.baseCSSPrefix + 'colorpicker',
      listeners : {
        scope : me,
        select : me.onSelect
      }
    });
    //picker.setValue(me.lastValue);
    return picker;
  },
  onSelect : function(picker, value) {
    var me = this, hex = '#' + value;

    me.setValue(hex);
    me.setFieldStyle({background: hex});
    me.fireEvent('select', me, hex);
    me.collapse();
  },

  onExpand : function(picker) {
    var me = this, value = me.getValue();
    me.picker.setValue(me.getValue());
  }
});

</script>
<script type="text/javascript">
Ext.onReady(function() {
    var m = [49, 20, 20, 19], // top right bottom left margin
    w = 1220 - m[1] - m[3], // width
    h = 200 - m[0] - m[2], // height
    z = 22; // cell size

var highColor = '#005500';
var lowColor = '#00FF00';

var highClipColor = '#FF0000';
var lowClipColor = '#0000FF';

var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    month = d3.time.format("%B"),
    percent = d3.format(".1%"),
    data,
    colors = {},
    formatDate = d3.time.format("%Y-%m-%d"),
    formatNumber = d3.format(",d"),
    formatPercent = d3.format("+.1%"),
    formatTime = d3.time.format.utc('%H:%M:%S'),
    selected_metric = 'fixes',
    metric_ranges = {};

var year_range = d3.range(${query['start'].year}, ${query['end'].year}+1);

var svg = d3.select("#years").selectAll(".year")
    .data(year_range)
  .enter().append("div")
    .attr("class", "year")
    .style("width", w + m[1] + m[3] + "px")
    .style("height", h + m[0] + m[2] + "px")
    .style("display", "inline-block")
  .append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + (m[3] + (w - z * 53) / 2) + "," + (m[0] + (h - z * 7) / 2) + ")");

svg.append("svg:text")
    .attr('class', 'title')
    .attr("transform", "translate(-6," + z * 3.5 + ")rotate(-90)")
    .attr("text-anchor", "middle")
    .text(String);

var rect = svg.selectAll("rect.day")
    .data(function(d) { return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("svg:rect")
    .attr("class", "day")
    .attr("width", z)
    .attr("height", z)
    .attr("x", function(d) { return week(d) * z; })
    .attr("y", function(d) { return day(d) * z; })
    ;

rect.append("svg:title");

var monthFormat = d3.time.format('%b');

svg.selectAll("path.month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
  .enter().append("svg:path")
    .attr("class", "month")
    .attr("d", monthPath)
;

svg.selectAll("text.month")
    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
    .enter().append('text')
        .attr("class", "month")
        .attr("y", -5)
        .attr("x", monthOffset)
        .text(monthFormat)
;

d3.select("select").on("change", function() {
    selected_metric = this.value;
    display(this.value);
});

d3.csv('${files['result.csv']}', function(csv) {
  var metrics = [
    'fixes',
    'distance',
    'accels',
    'maxalt', 'avgalt', 'minalt',
    'maxtemp', 'avgtemp', 'mintemp',
    'minvbat',
    'maxgpsinterval', 'mingpsinterval'
  ];

  // Parse dates, numbers and handle NA's
  csv.forEach(function(d) {
      d.date = formatDate.parse(d.date);
      metrics.forEach(function(m) {
          if (d[m] === 'NA') {
              d[m] = null;
          } else {
              d[m] = +d[m];
          }
      });
  });

  // Make color scales
  metrics.forEach(function(m) {
      metric_ranges[m] = d3.extent(csv, function(d) { return d[m]; })
      colors[m] =  d3.scale.linear().domain(metric_ranges[m]).interpolate(d3.interpolateRgb).range([lowColor, highColor]);
  });

  // Group data per year
  data = d3.nest()
      .key(function(d) { return d.date.getFullYear(); })
      .key(function(d) { return d.date; })
      .rollup(function(d) {
          var r = {};
          metrics.forEach(function(m) {
              r[m] = d[0][m];
          });
          return r;
      })
      .map(csv);

  display('fixes');
});

function clipped_display(metric, clip_low, clip_high) {
    var color = colors[metric];
    color.domain([clip_low, clip_high]);

    function formatMetricValue(value) {
        if (value === null) {
            return 'NA';
        }
        if (metric === 'maxgpsinterval' || metric === 'mingpsinterval') {
            value = new Date(value*1000);
            // Interval can be longer than one day, so prepend number of days
            if (value < (1000*60*60*24)) {
                return formatTime(value);
            } else {
                var day_part = formatTime(value);
                var days = Math.floor(value/(1000*60*60*24));
                return days + " days " + day_part;
            }
        }
        return value;
    }

    svg.each(function(year) {
      d3.select(this).selectAll("rect.day")
        .attr("class", "day")
        .attr("style", function(d) {
            if (year in data && d in data[year]) {
                if (data[year][d][metric] === null) {
                  return 'fill: lightgray;';
                } else {
                  if (data[year][d][metric] < color.domain()[0]) {
                      return 'fill:' + lowClipColor + ';';
                  } else if (data[year][d][metric] > color.domain()[1]) {
                      return 'fill:' + highClipColor + ';';
                  } else {
                      return 'fill:' + color(data[year][d][metric]) + ';';
                  }
                }
            }
        })
        .select("title")
          .text(function(d) {
              if (year in data && d in data[year]) {
                  return formatDate(d) + ": " + formatMetricValue(data[year][d][metric]);
              } else {
                  return formatDate(d) + ": NA";
              }
          });
    });

    d3.select('#legend').select('#low_label').text(formatMetricValue(clip_low));
    d3.select('#legend').select('#high_label').text(formatMetricValue(clip_high));
}

function display(metric) {
  var color = colors[metric];
  // Reset color domain
  color.domain(metric_ranges[metric]);
  slider.setMinValue(color.domain()[0]);
  slider.setMaxValue(color.domain()[1]);
  slider.setValue(color.domain(), false);

  clipped_display(metric, color.domain()[0], color.domain()[1]);
}

var lw = 200;
var lh = 20;
var legend = d3.select("#legend").append('svg')
  .attr('width', lw)
  .attr('height', lh + 30);

var gradient = legend.append("defs")
.append("linearGradient")
  .attr("id", "gradient")
  .attr("x1", "0%")
  .attr("y1", "0%")
  .attr("x2", "100%")
  .attr("y2", "0%")
  .attr("spreadMethod", "pad");

gradient.append("stop")
  .attr("class", "low")
  .attr("offset", "0%")
  .attr("stop-color", lowColor)
  .attr("stop-opacity", 1);

gradient.append("stop")
  .attr("class", "high")
  .attr("offset", "100%")
  .attr("stop-color", highColor)
  .attr("stop-opacity", 1);

legend.append("rect")
  .attr("width", lw)
  .attr("height", lh)
  .style("fill", "url(#gradient)");

var g = legend.append('g');

g.append("text")
 .attr('id', 'high_label')
 .attr('x', 200)
 .attr('y', 40)
 .attr('text-anchor', 'end')
 .text('High');

g.append("text")
 .attr('id', 'low_label')
 .attr('x', 0)
 .attr('y', 40)
 .text('Low');

function monthOffset(t0) {
    var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
    d0 = +day(t0), w0 = +week(t0),
    d1 = +day(t1), w1 = +week(t1);
    return  (w0 + 1) * z;
}

function monthPath(t0) {
  var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
      d0 = +day(t0), w0 = +week(t0),
      d1 = +day(t1), w1 = +week(t1);
  return "M" + (w0 + 1) * z + "," + d0 * z
      + "H" + w0 * z + "V" + 7 * z
      + "H" + w1 * z + "V" + (d1 + 1) * z
      + "H" + (w1 + 1) * z + "V" + 0
      + "H" + (w0 + 1) * z + "Z";
}

var slider;
slider = Ext.create('Ext.slider.Multi', {
    width: 200,
    values: [0, 100],
    //increment: 5,
    minValue: 0,
    maxValue: 100,
    decimalPrecision: 3,
    renderTo: 'slider',
    useTips: false,
    listeners: {
        change: function(comp) {
            var clip_low = slider.getValue(0);
            var clip_high = slider.getValue(1);
            clipped_display(selected_metric, clip_low, clip_high);
        }
    }
});

function changeLowColor(picker, newColor) {
    lowColor = newColor;
    Object.keys(colors).forEach(function(metric) {
        var range = colors[metric].range();
        range[0] = lowColor;
        colors[metric].range(range);
    });
    gradient.select('stop.low').attr("stop-color", lowColor);
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
}

function changeHighColor(picker, newColor) {
    highColor = newColor;
    Object.keys(colors).forEach(function(metric) {
        var range = colors[metric].range();
        range[1] = highColor;
        colors[metric].range(range);
    });
    gradient.select('stop.high').attr("stop-color", highColor);
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
}

function changeLowClipColor(picker, newColor) {
    lowClipColor = newColor;
    if (!(selected_metric in colors)) return ;
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
}

function changeHighClipColor(picker, newColor) {
    highClipColor = newColor;
    if (!(selected_metric in colors)) return ;
    var clip_low = slider.getValue(0);
    var clip_high = slider.getValue(1);
    clipped_display(selected_metric, clip_low, clip_high);
}

var colorPanel = Ext.create('Ext.window.Window', {
  title: 'Alter colors',
  height: 150,
  width: 250,
  layout: 'form',
  x: 50,
  y: 50,
  closeAction: 'hide',
  bodyPadding: 5,
  defaults: {
    xtype: 'ux.colorpickerfield'
  },
  items: [{
    fieldLabel: 'Lowest',
    fieldStyle: 'background: ' + lowColor,
    value: lowColor,
    listeners: {
      change: changeLowColor
    }
  }, {
    fieldLabel: 'Highest',
    fieldStyle: 'background: ' + highColor,
    value: highColor,
    listeners: {
      change: changeHighColor
    }
  }, {
    fieldLabel: 'Below lowest',
    fieldStyle: 'background: ' + lowClipColor,
    value: lowClipColor,
    listeners: {
      change: changeLowClipColor
    }
  }, {
    fieldLabel: 'Above Highest',
    fieldStyle: 'background: ' + highClipColor,
    value: highClipColor,
    listeners: {
      change: changeHighClipColor
    }
  }]
});

Ext.create('Ext.Button', {
    text: 'Colors ...',
    renderTo: 'colorpanel',
    handler: function() {
        colorPanel.show();
    }
});

});

</script>
