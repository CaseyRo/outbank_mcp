## ADDED Requirements

### Requirement: README includes Outbank affiliate disclosure
The README SHALL include the Outbank affiliate link with a clear disclosure that the link is an affiliate referral.

#### Scenario: Reader views README footer
- **WHEN** the reader scrolls to the Outbank section near the end of the README
- **THEN** the affiliate link and disclosure are visible together

### Requirement: README avoids redundant app store badges
The README SHALL omit App Store and Google Play badge markup when the affiliate link page already provides download options.

#### Scenario: Reader scans the README
- **WHEN** the reader looks for download badges
- **THEN** the App Store and Google Play badges are not present

### Requirement: README notes under-construction status
The README SHALL include an under-construction note stating the purpose for the affiliate link is not finalized yet.

#### Scenario: Reader checks project status
- **WHEN** the reader reaches the README footer notes
- **THEN** the under-construction note mentions the unclear current reason for the affiliate link
