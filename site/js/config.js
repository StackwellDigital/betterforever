/*
 * Better Forever - site configuration. This is the ONLY file you need to edit to wire up booking.
 *
 * JANE APP BOOKING
 *   general:       the clinic's main online booking page (used by every generic "Book Now" button)
 *   practitioners: optional per-practitioner booking pages. Any key left "" falls back to `general`.
 *   Jane URLs look like  https://<clinic>.janeapp.com/  and  https://<clinic>.janeapp.com/locations/<location>/book
 *   Staff pages look like https://<clinic>.janeapp.com/locations/<location>/book#/staff_member/<id>
 *
 *   Until `general` is filled in, every Book Now button falls back to the on-site /book/ page
 *   (practitioner list plus the "I'm just starting" form), so the demo never has a dead link.
 *
 * INQUIRY FORMS
 *   inquiryEndpoint: URL that accepts a JSON POST (Formspree, Cloudflare Pages Function, etc).
 *   Left empty, the forms open the visitor's email app addressed to `inquiryEmail`.
 */
window.BF_CONFIG = {
  jane: {
    general: "",
    practitioners: {
      berghamer: "",
      kawamoto: "",
      joel: "",
      cam: "",
      marina: ""
    }
  },
  inquiryEndpoint: "",
  inquiryEmail: "admin@betterforever.ca"
};
