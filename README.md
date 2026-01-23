# [DailySpeakUp](https://dailyspeak.app/)

## Opis projekta

Ovaj projekt je rezultat timskog rada u sklopu projektnog zadatka kolegija [Programsko inženjerstvo](https://www.fer.unizg.hr/predmet/proinz) na Fakultetu elektrotehnike i računarstva Sveučilišta u Zagrebu.

U današnjem poslovnom i akademskom okruženju, sposobnost jasnog i uvjerljivog izražavanja ključna je kompetencija. Mnogi studenti i profesionalci suočavaju se s poteškoćama u javnom govoru, prezentacijama i spontanoj komunikaciji. Postojeća rješenja često zahtijevaju mentore ili skupu obuku, a self-paced alati nisu dovoljno strukturirani.

DailySpeakUp pruža pristupačno, gamificirano rješenje koje omogućava svakodnevno vježbanje kroz kratke jednominutne govorne izazove, s mogućnošću praćenja napretka i dobivanja povratnih informacija od zajednice.

## Članovi tima

* [Emil Popović](https://github.com/EmilPopovic) - voditelj, arhitektura, backend
* [Matej Jurasić](https://github.com/cappig) - backend, testiranje
* [Lara Brečić](https://github.com/Lara7260) - frontend
* [Mate Jakovljev](https://github.com/mate7589) - frontend
* [Kristijan Bilanović](https://github.com/KristijanBilanovic) - frontend, testiranje
* [Lara Desnica](https://github.com/LaraDesnica) - dokumentacije
* [Nika Valić](https://github.com/wavetoc520) - UI/UX

## Osnovne informacije i korištenje

Aplikacija je dostupna na [dailyspeak.app](https://dailyspeak.app).

### Registracija i prijava

Za korištenje je potreban pristup Google računu ili bilo kojoj drugoj mail adresi. U sustav se prijavljuje klikom na gumb "Log in" na početnoj stranici, nakon čega se otvara _modal_ za prijavu. Prijava putem Googlea prijavljuje korisnika odmah nakon Googleove potvrde. Ako se koristi druga email adresa, bit će poslan mail s linkom (gumbom) za prijavu.

Novom se korisniku nakon registracije šalje mail dobrodošlice na odabranu adresu. To znači da je račun uspješno kreiran.

Unutar aplikacije, prijavljeni se korisnik može odjaviti klikom na ikonu korisnika (gore desno u navigacijskoj traci), te potom klikom na gumb "Log out".

### Onboarding

Nakon registracije, korisnik prolazi onboarding - bira ime koje se prikazuje u aplikaciji (_display name_), jedinstvenu oznaku korisnika (_handle_) te interese.

Prijavljeni korisnik nema pristup ostatku aplikacije dok nije prošao onboarding.

### Generiranje teme

Prijavljeni korisnik klikom na gumb na početnoj stranici generira temu za svoj govor. Ako je slučajno kliknuo na gumb, unutar određenog vremena ga može opet stisnuti kako bi otkazao generiranje teme.

Tema je temeljena na nasumično izabranom interesu tog korisnika, a prikazuje se u polju teme na dnu početne stranice.

## Tehnologije

### Tech stack

* Backend: [FastAPI](https://fastapi.tiangolo.com/)
* Frontend: [Vue.js](https://vuejs.org/)
* Baza podataka: [PostgreSQL](https://www.postgresql.org/) (hostano na [neon.com](https://neon.com))
* Deployment: [Hetzner VPS](https://www.hetzner.com/) + [Dokploy](https://dokploy.com/)

### Vanjske usluge

* AI servis za generiranje tema: [Google Gemini](https://gemini.google/about/)
* Autentikacija: [SuperTokens](https://supertokens.com/)
* Push notifikacije: [Firebase Cloud Messaging](https://firebase.google.com/products/cloud-messaging)
* Video pohrana: [Cloudflare R2](https://www.cloudflare.com/products/r2/)
* Email usluge: [Resend](https://resend.com/)

## Kontribucije

Tijekom rada na projektu potrebno je pridržavati se kodeksa ponašanja i etičkog kodeksa projekta. Detaljnije informacije dostupne su u datoteci [CONTRIBUTING.md](https://github.com/progi-2025-g8-1/daily-speak-up/blob/main/CONTRIBUTING.md). 

## Licenca

Ovaj projekt je licenciran pod GNU General Public License licencom. Pogledajte [LICENSE](https://github.com/progi-2025-g8-1/daily-speak-up/blob/main/LICENSE) datoteku za više informacija.
