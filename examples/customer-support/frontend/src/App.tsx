import { useMemo, useRef, useState } from "react";
import clsx from "clsx";
import {
  ArrowLeft,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  LogIn,
  Mail,
  Search,
} from "lucide-react";
import { CxChatWidget } from "./components/CxChatWidget";
import type { ChatHandoffContext } from "./components/CxChatWidget";

type AuthState = "logged_in" | "logged_out";
type FieldType = "text" | "email" | "tel" | "textarea" | "select" | "resource";

type ResourceOption = {
  id: string;
  title: string;
  seller: string;
  accent: string;
};

type FieldConfig = {
  id: string;
  label: string;
  type: FieldType;
  placeholder?: string;
  options?: string[];
  required?: boolean;
  resourceForGuests?: boolean;
  helperText?: string;
};

type FlowConfig = {
  label: string;
  summary: string;
  subject: string;
  tags: string[];
  backendNote?: string;
  csvIntake?: string;
  baseFields: FieldConfig[];
  conditionalFields?: Array<{
    when: (values: FormValues) => boolean;
    fields: FieldConfig[];
  }>;
};

type CategoryConfig = {
  description: string;
  issues: FlowConfig[];
};

type FlowMap = Record<string, CategoryConfig>;
type FormValues = Record<string, string>;

type SubmissionPayload = {
  authState: AuthState;
  isGuest: boolean;
  parentTopic: string;
  issue: string;
  subject: string;
  tags: string[];
  name: string | null;
  email: string | null;
  fields: FormValues;
  backendLogic?: string;
  chatbotHandoff?: ChatHandoffContext | null;
};

const MOCK_RESOURCES: ResourceOption[] = [
  {
    id: "resource-phonics",
    title: "Phonics Centers Mega Pack",
    seller: "Mrs. Alvarez's Classroom",
    accent: "from-emerald-300 via-teal-200 to-white",
  },
  {
    id: "resource-fractions",
    title: "Fraction Escape Room",
    seller: "Math with Mr. D",
    accent: "from-lime-200 via-emerald-100 to-white",
  },
  {
    id: "resource-science",
    title: "Ecosystems Interactive Notebook",
    seller: "Science and Sprinkles",
    accent: "from-teal-200 via-cyan-100 to-white",
  },
  {
    id: "resource-social",
    title: "Revolutionary War Timeline",
    seller: "Primary Source Studio",
    accent: "from-green-200 via-emerald-100 to-white",
  },
];

const GUEST_FIELDS: FieldConfig[] = [
  {
    id: "guest_name",
    label: "Full name",
    type: "text",
    placeholder: "Enter your name",
    required: true,
  },
  {
    id: "guest_email",
    label: "Account email",
    type: "email",
    placeholder: "name@email.com",
    required: true,
  },
];

const LOGGED_IN_PROFILE = {
  name: "Will E",
  email: "will+demo@ixl.com",
};

const FLOW_DATA: FlowMap = {
  "Orders & Refunds": {
    description:
      "Help buyers recover purchases, request credits, or resolve gift card and promo-code problems.",
    issues: [
      {
        label: "Refund Request",
        summary:
          "Guide buyers through a more precise refund request with reason capture and resource context.",
        subject: "Refund Request",
        tags: ["ada", "refund_request", "ada_first_response"],
        csvIntake:
          "For most - Resource Selection, Refund Reason (Dropdown), Error Details (Conditional); For bundle 2x resource selection; For Seller, name of Buyer or Order ID, reason for requesting refund",
        baseFields: [
          {
            id: "resource_selection",
            label: "Resource selection",
            type: "resource",
            required: true,
            resourceForGuests: true,
          },
          {
            id: "refund_reason",
            label: "Refund reason",
            type: "select",
            options: [
              "Technical Error",
              "Missing Content",
              "Duplicate Purchase",
              "Wrong Resource",
              "Bundle Issue",
              "Seller Requested",
            ],
            required: true,
          },
          {
            id: "bundle_resource_selection",
            label: "Second resource in bundle",
            type: "resource",
            resourceForGuests: true,
            placeholder: "Add a second bundle item if relevant",
          },
          {
            id: "buyer_name_or_order_id",
            label: "Buyer name or order ID",
            type: "text",
            placeholder: "Only needed for seller-led requests",
          },
          {
            id: "refund_context",
            label: "Anything else we should know?",
            type: "textarea",
            placeholder: "Share the context for your refund request",
            required: true,
          },
        ],
        conditionalFields: [
          {
            when: (values) =>
              values.refund_reason === "Technical Error" ||
              values.refund_reason === "Missing Content",
            fields: [
              {
                id: "error_details",
                label: "Please describe the error",
                type: "textarea",
                placeholder:
                  "Tell us what happened, what you expected, and any error message shown",
                required: true,
              },
            ],
          },
        ],
      },
      {
        label: "Missing Purchases",
        summary:
          "Verify missing purchases by matching billing details and account ownership.",
        subject: "Missing Purchases",
        tags: [
          "ada",
          "buyer_questions",
          "duplicate_accounts",
          "ada_first_response",
        ],
        backendNote: "Search DB by billing info.",
        csvIntake: "Phone Number, Street Address, Account Email",
        baseFields: [
          {
            id: "phone_number",
            label: "Phone number",
            type: "tel",
            required: true,
          },
          {
            id: "street_address",
            label: "Street address",
            type: "text",
            required: true,
          },
          {
            id: "account_email",
            label: "Account email",
            type: "email",
            required: true,
          },
        ],
      },
      {
        label: "Forgot Promo Code",
        summary:
          "Capture order context for promo-code recovery or TPT credit handling.",
        subject: "Forgot Promo Code",
        tags: ["ada", "refund_request", "ada_first_response"],
        backendNote: "v3: Auto-issue TPT Credits.",
        csvIntake: "Order Number, Promo Code Name",
        baseFields: [
          {
            id: "order_number",
            label: "Order number",
            type: "text",
            required: true,
          },
          {
            id: "promo_code_name",
            label: "Promo code name",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Lost Gift Card",
        summary: "Recover a missing gift card for the sender or recipient.",
        subject: "Gift Card Question",
        tags: ["ada", "other", "ada_first_response"],
        backendNote: "Verify balance in DB.",
        csvIntake: "Sent or Received Gift Card, Your Email, Email of Recipient",
        baseFields: [
          {
            id: "gift_card_role",
            label: "Was the gift card sent or received?",
            type: "select",
            options: ["Sent Gift Card", "Received Gift Card"],
            required: true,
          },
          {
            id: "your_email",
            label: "Your email",
            type: "email",
            required: true,
          },
          {
            id: "recipient_email",
            label: "Recipient email",
            type: "email",
            required: true,
          },
        ],
      },
    ],
  },
  "Login & Access": {
    description:
      "Handle account ownership, verification, merges, and login recovery with the right identity checks.",
    issues: [
      {
        label: "No Access to Account Email",
        summary:
          "Collect updated contact information for account recovery without access to the original inbox.",
        subject: "TPT Login Support without Access to Account Email",
        tags: ["ada", "login_or_password_issues", "ada_first_response"],
        backendNote: "v3: Identity verification reset.",
        csvIntake: "Current Email, New Email (Text), Phone, Street Address",
        baseFields: [
          {
            id: "current_email",
            label: "Current email on file",
            type: "email",
            required: true,
          },
          {
            id: "new_email",
            label: "New email",
            type: "email",
            required: true,
          },
          {
            id: "phone_number",
            label: "Phone number",
            type: "tel",
            required: true,
          },
          {
            id: "street_address",
            label: "Street address",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Merge Two Accounts",
        summary:
          "Verify two accounts and collect the exact account details needed for a safe merge.",
        subject: "Merge TPT Accounts Request",
        tags: [
          "ada",
          "merge_accounts_1",
          "username",
          "account_settings",
          "my_account",
          "ada_first_response",
        ],
        backendNote: "Identity verification merge.",
        csvIntake:
          "Email 1 (you'd like to use moving forward), Email 2 (Text), Phone & Address (for both)",
        baseFields: [
          {
            id: "primary_account_email",
            label: "Email to keep moving forward",
            type: "email",
            required: true,
          },
          {
            id: "secondary_account_email",
            label: "Second account email",
            type: "email",
            required: true,
          },
          {
            id: "primary_account_phone",
            label: "Phone for account 1",
            type: "tel",
            required: true,
          },
          {
            id: "primary_account_address",
            label: "Address for account 1",
            type: "text",
            required: true,
          },
          {
            id: "secondary_account_phone",
            label: "Phone for account 2",
            type: "tel",
            required: true,
          },
          {
            id: "secondary_account_address",
            label: "Address for account 2",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "OTP / Verification Issue",
        summary: "Resolve one-time password and verification failures.",
        subject: "One Time Password Login Support",
        tags: [
          "ada",
          "login_or_password_issues",
          "ada_first_response",
          "otp_cx",
        ],
        backendNote: "SMS service re-sync.",
        csvIntake: "Phone Number, Street Address, Account Email",
        baseFields: [
          {
            id: "phone_number",
            label: "Phone number",
            type: "tel",
            required: true,
          },
          {
            id: "street_address",
            label: "Street address",
            type: "text",
            required: true,
          },
          {
            id: "account_email",
            label: "Account email",
            type: "email",
            required: true,
          },
        ],
      },
      {
        label: "How to Close Account",
        summary: "Capture closure intent before deactivation or downgrade.",
        subject: "Close or Downgrade Account",
        tags: ["ada", "my_account", "ada_first_response"],
        backendNote: "v3: Auto-deactivation.",
        csvIntake: "Desired account type, Reason for closure, Confirmation Toggle",
        baseFields: [
          {
            id: "desired_account_type",
            label: "Desired account type",
            type: "select",
            options: ["Close Buyer Account", "Close Seller Account", "Downgrade Seller"],
            required: true,
          },
          {
            id: "closure_reason",
            label: "Reason for closure",
            type: "textarea",
            placeholder: "Tell us why you want to close or downgrade the account",
            required: true,
          },
          {
            id: "closure_confirmation",
            label: "Confirm you want us to contact you about closure",
            type: "select",
            options: ["Yes, confirm", "Not yet"],
            required: true,
          },
        ],
      },
      {
        label: "Publisher Account",
        summary: "General support for publisher account workflows.",
        subject: "Publisher Account Question",
        tags: ["ada", "ada_first_response", "publisher_account_bot", "my_account"],
        baseFields: [
          {
            id: "publisher_question",
            label: "What do you need help with?",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Password Reset Support",
        summary: "Triage a password reset issue when the account email is accessible.",
        subject: "TPT Login Support with Access to Account Email",
        tags: ["ada", "login_or_password_issues", "ada_first_response"],
        backendNote: "v3: Identity verification reset.",
        baseFields: [
          {
            id: "account_email",
            label: "Account email",
            type: "email",
            required: true,
          },
          {
            id: "reset_issue",
            label: "What is going wrong?",
            type: "textarea",
            placeholder: "For example: reset email never arrives, link expired, or link fails",
            required: true,
          },
        ],
      },
    ],
  },
  "TPT School Express": {
    description:
      "Support school and district buyers using TPT School Express workflows.",
    issues: [
      {
        label: "TPT School Express",
        summary: "General support for TPT School Express purchasing flows.",
        subject: "TPT School Express Question",
        tags: ["ada", "ada_first_response", "tpt_school_express", "sx_bot"],
        baseFields: [
          {
            id: "school_name",
            label: "School or district name",
            type: "text",
            required: true,
          },
          {
            id: "quote_id",
            label: "Quote ID",
            type: "text",
            placeholder: "Optional if you have one",
          },
          {
            id: "po_number",
            label: "PO number",
            type: "text",
            placeholder: "Optional if you have one",
          },
          {
            id: "school_express_question",
            label: "How can we help?",
            type: "textarea",
            required: true,
          },
        ],
      },
    ],
  },
  "Seller Store": {
    description:
      "Support sellers with payout, listing, premium, and account-adjacent questions.",
    issues: [
      {
        label: "Payout Issue",
        summary: "Investigate seller payout and Hyperwallet delivery problems.",
        subject: "Hyperwallet Payout Question",
        tags: ["ada", "payouts", "ada_first_response", "hyperwallet", "hw_payout"],
        backendNote: "v3: Check Hyperwallet API.",
        csvIntake: "Store URL, Payment Email, Payout Method",
        baseFields: [
          {
            id: "store_url",
            label: "Store URL",
            type: "text",
            required: true,
          },
          {
            id: "payment_email",
            label: "Payment email",
            type: "email",
            required: true,
          },
          {
            id: "payout_method",
            label: "Payout method",
            type: "select",
            options: ["Hyperwallet", "PayPal", "Bank Transfer"],
            required: true,
          },
        ],
      },
      {
        label: "Hyperwallet Registration",
        summary: "Capture a seller registration problem for Hyperwallet onboarding.",
        subject: "Hyperwallet Registration Question",
        tags: ["ada", "payouts", "ada_first_response", "hyperwallet", "hw_registration"],
        baseFields: [
          {
            id: "registration_issue",
            label: "What issue are you seeing?",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Premium Renewal Trouble",
        summary: "Resolve seller premium renewal issues and billing confusion.",
        subject: "Premium Membership Question",
        tags: ["ada", "payouts", "ada_first_response"],
        baseFields: [
          {
            id: "renewal_question",
            label: "Describe the renewal problem",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Inactive Listing",
        summary: "Investigate a resource that appears inactive or unavailable.",
        subject: "Product Status Question",
        tags: ["ada", "other", "ada_first_response", "inactive_resource_review"],
        backendNote: 'Check "Inactive" DB status.',
        csvIntake: "Store URL, Resource Selection",
        baseFields: [
          {
            id: "store_url",
            label: "Store URL",
            type: "text",
            required: true,
          },
          {
            id: "resource_selection",
            label: "Resource selection",
            type: "resource",
            required: true,
            resourceForGuests: true,
          },
        ],
      },
      {
        label: "Seller Estate Planning",
        summary:
          "Route sensitive estate planning or passing-related seller account questions.",
        subject: "Estate Planning Question",
        tags: [
          "ada",
          "escalation_marketplaceintegrity",
          "rules__policies__and_guidelines",
          "ada_first_response",
        ],
        baseFields: [
          {
            id: "estate_context",
            label: "Recent passing or estate planning details",
            type: "textarea",
            required: true,
          },
        ],
      },
    ],
  },
  "Quality & Safety": {
    description:
      "Handle feedback moderation, unauthorized charges, and product-quality requests.",
    issues: [
      {
        label: "Feedback Removal",
        summary: "Submit a review for moderation with precise product context.",
        subject: "Feedback Removal Question",
        tags: [
          "ada",
          "feedback_and_ratings",
          "ada_first_response",
          "feedback_trigger_mi",
        ],
        csvIntake: "Resource Selection, Copy of Review, Reason",
        baseFields: [
          {
            id: "resource_selection",
            label: "Resource selection",
            type: "resource",
            required: true,
            resourceForGuests: true,
          },
          {
            id: "review_copy",
            label: "Copy of review",
            type: "textarea",
            required: true,
          },
          {
            id: "removal_reason",
            label: "Reason for removal",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Suggestion",
        summary: "Collect detailed product or platform feedback for the product team.",
        subject: "Product Suggestion",
        tags: ["ada", "suggestions", "ada_first_response"],
        backendNote: "Copy to Product team?",
        csvIntake: "Detailed Feedback",
        baseFields: [
          {
            id: "detailed_feedback",
            label: "Detailed feedback",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Unauthorized Purchase",
        summary:
          "Gather payment details needed to investigate an unauthorized purchase.",
        subject: "Unauthorized Purchase Question",
        tags: [
          "ada",
          "escalation_marketplaceintegrity",
          "my_account",
          "ada_first_response",
        ],
        csvIntake: "Date of Charge, Amount, Last 4 of Card / PayPal Email",
        baseFields: [
          {
            id: "date_of_charge",
            label: "Date of charge",
            type: "text",
            placeholder: "MM/DD/YYYY",
            required: true,
          },
          {
            id: "charge_amount",
            label: "Amount",
            type: "text",
            required: true,
          },
          {
            id: "payment_reference",
            label: "Last 4 of card or PayPal email",
            type: "text",
            required: true,
          },
        ],
      },
    ],
  },
  "Technical Issues": {
    description:
      "Triage resource errors, Google Drive failures, and broader site issues with enough detail to debug.",
    issues: [
      {
        label: "Google Drive Resources",
        summary: "Troubleshoot online resources that rely on Google integrations.",
        subject: "Online Resource Support",
        tags: [
          "ada",
          "ada_first_response",
          "online_resources",
          "technical_issue_with_a_resource",
        ],
        backendNote: "v3: Check API permissions.",
        csvIntake: "Resource Selection, Google Account Email, what steps have you taken",
        baseFields: [
          {
            id: "resource_selection",
            label: "Resource selection",
            type: "resource",
            required: true,
            resourceForGuests: true,
          },
          {
            id: "google_account_email",
            label: "Google account email",
            type: "email",
            required: true,
          },
          {
            id: "troubleshooting_steps",
            label: "What steps have you taken?",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Report a Site Issue",
        summary: "Capture an actionable site bug report for engineering.",
        subject: "Report a Site Issue",
        tags: ["ada", "report_a_site_issue", "ada_first_response"],
        backendNote: "Log to Engineering.",
        csvIntake:
          "Where on the site /URL of error, What's happening? Browser/OS info, Screenshot",
        baseFields: [
          {
            id: "site_location",
            label: "Where on the site is the issue?",
            type: "text",
            placeholder: "Page name or URL",
            required: true,
          },
          {
            id: "site_issue_description",
            label: "What's happening?",
            type: "textarea",
            required: true,
          },
          {
            id: "browser_os",
            label: "Browser and OS info",
            type: "text",
            placeholder: "Chrome on macOS, Safari on iPhone, etc.",
            required: true,
          },
          {
            id: "screenshot_note",
            label: "Screenshot note",
            type: "textarea",
            placeholder: "Describe the screenshot or note what you'd attach",
            required: true,
          },
        ],
      },
      {
        label: "Resource Tech Issue",
        summary: "Report a product-specific technical issue with the resource.",
        subject: "Resource Tech Issue",
        tags: ["ada", "technical_issue_with_a_resource", "ada_first_response"],
        csvIntake: "Resource Selection, Problem Description",
        baseFields: [
          {
            id: "resource_selection",
            label: "Resource selection",
            type: "resource",
            required: true,
            resourceForGuests: true,
          },
          {
            id: "problem_description",
            label: "Problem description",
            type: "textarea",
            required: true,
          },
        ],
      },
    ],
  },
  "School Purchase Orders / Schools Purchasing": {
    description:
      "Support districts and schools with quote, invoice, tax, and purchase-order workflows.",
    issues: [
      {
        label: "Sales Tax Refund",
        summary: "Request a sales tax refund tied to an existing order.",
        subject: "Sales Tax Refund Request",
        tags: ["ada", "refund_request", "ada_first_response", "sales_tax_refund"],
        csvIntake: "Order ID",
        baseFields: [
          {
            id: "order_id",
            label: "Order ID",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Order Processing Update",
        summary: "Check current progress for an existing quote or purchase order.",
        subject: "Purchase Order Status",
        tags: ["ada", "school_purchase_orders", "ada_first_response"],
        backendNote: "Fetch Real-time Order Status.",
        csvIntake: "Quote ID, PO number",
        baseFields: [
          {
            id: "quote_id",
            label: "Quote ID",
            type: "text",
            required: true,
          },
          {
            id: "po_number",
            label: "PO number",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Editing Quotes",
        summary: "Request changes to a school quote before processing.",
        subject: "Edit Quote Request",
        tags: ["ada", "school_purchase_orders", "ada_first_response"],
        csvIntake: "Quote ID, List of changes needed",
        baseFields: [
          {
            id: "quote_id",
            label: "Quote ID",
            type: "text",
            required: true,
          },
          {
            id: "quote_changes",
            label: "List of changes needed",
            type: "textarea",
            required: true,
          },
        ],
      },
      {
        label: "Administrator Receipt Request",
        summary: "Investigate or re-send a receipt for an administrator purchase.",
        subject: "Administrator Receipt Request",
        tags: ["ada", "my_account", "ada_first_response"],
        csvIntake: "Date of Charge, Amount, Last 4 of Card / PayPal Email",
        baseFields: [
          {
            id: "date_of_charge",
            label: "Date of charge",
            type: "text",
            placeholder: "MM/DD/YYYY",
            required: true,
          },
          {
            id: "charge_amount",
            label: "Amount",
            type: "text",
            required: true,
          },
          {
            id: "payment_reference",
            label: "Last 4 of card or PayPal email",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Apply Tax Exempt Status",
        summary: "Collect school information needed to apply tax exemption.",
        subject: "Apply School Tax Exemption",
        tags: ["ada", "school_purchase_orders", "ada_first_response"],
        csvIntake: "School Name, School District, State",
        baseFields: [
          {
            id: "school_name",
            label: "School name",
            type: "text",
            required: true,
          },
          {
            id: "school_district",
            label: "School district",
            type: "text",
            required: true,
          },
          {
            id: "state",
            label: "State",
            type: "text",
            required: true,
          },
        ],
      },
      {
        label: "Invoice Request",
        summary: "Request an invoice using the quote and purchase order reference.",
        subject: "Invoice Request",
        tags: ["ada", "school_purchase_orders", "ada_first_response"],
        csvIntake: "Quote ID, PO number",
        baseFields: [
          {
            id: "quote_id",
            label: "Quote ID",
            type: "text",
            required: true,
          },
          {
            id: "po_number",
            label: "PO number",
            type: "text",
            required: true,
          },
        ],
      },
    ],
  },
};

function App() {
  const categoryEntries = Object.entries(FLOW_DATA);
  const [authState, setAuthState] = useState<AuthState>("logged_in");
  const [isGuest, setIsGuest] = useState(false);
  const [selectedParent, setSelectedParent] = useState<string>("");
  const [selectedIssueLabel, setSelectedIssueLabel] = useState<string>("");
  const [formValues, setFormValues] = useState<FormValues>({});
  const [openResourceFieldId, setOpenResourceFieldId] = useState<string | null>(null);
  const [submittedPayload, setSubmittedPayload] = useState<SubmissionPayload | null>(
    null,
  );
  const [chatbotHandoff, setChatbotHandoff] = useState<ChatHandoffContext | null>(
    null,
  );
  const intakeSectionRef = useRef<HTMLElement | null>(null);

  const activeCategory = FLOW_DATA[selectedParent];
  const activeIssue =
    activeCategory?.issues.find((issue) => issue.label === selectedIssueLabel) ??
    null;
  const currentStep = selectedIssueLabel ? 3 : selectedParent ? 2 : 1;

  const visibleFields = useMemo(() => {
    if (!activeIssue) {
      return [];
    }

    const guestAwareBase = activeIssue.baseFields.flatMap((field) => {
      if (field.type === "resource" && authState === "logged_out") {
        if (!isGuest) {
          return [];
        }

        if (field.resourceForGuests) {
          return [
            {
              ...field,
              id: `${field.id}_guest_url`,
              label: "Resource URL",
              type: "text" as const,
              placeholder: "Paste the TPT resource URL",
            },
          ];
        }
      }

      return [field];
    });

    const guestFields = authState === "logged_out" && isGuest ? GUEST_FIELDS : [];
    const conditionalFields =
      activeIssue.conditionalFields
        ?.filter((group) => group.when(formValues))
        .flatMap((group) => group.fields) ?? [];

    return [...guestFields, ...guestAwareBase, ...conditionalFields];
  }, [activeIssue, authState, formValues, isGuest]);

  const loggedInIdentity = authState === "logged_in" ? LOGGED_IN_PROFILE : null;

  const issueIntroCopy = useMemo(() => {
    if (!activeIssue) {
      return {
        title: "Tell us a little more",
        description:
          "Share the details we need so we can help with your request.",
      };
    }

    const copyByIssue: Record<string, { title: string; description: string }> = {
      "No Access to Account Email": {
        title: "Let’s help you get back into your account",
        description:
          "Before we can help reset account access, we need to confirm a few details to protect your information.",
      },
      "Refund Request": {
        title: "Tell us about your refund request",
        description:
          "Please share the purchase details and the reason for your request so our team can review it.",
      },
      "Merge Two Accounts": {
        title: "Help us confirm both accounts",
        description:
          "We’ll need details for each account so we can review your merge request safely.",
      },
      "Missing Purchases": {
        title: "Let’s find your purchase",
        description:
          "Please share the account and billing details below so we can look into the missing order.",
      },
      "OTP / Verification Issue": {
        title: "Let’s verify your account details",
        description:
          "We need a few account details so we can review the verification issue and help restore access.",
      },
      "Password Reset Support": {
        title: "Tell us what’s happening with your password reset",
        description:
          "Share the account details and what you’re seeing so we can help troubleshoot the reset flow.",
      },
      "Feedback Removal": {
        title: "Tell us about the feedback you’d like reviewed",
        description:
          "Please include the resource and the review details so our team can take a closer look.",
      },
      "Report a Site Issue": {
        title: "Help us understand the site issue",
        description:
          "The more detail you can share about where this happened and what you saw, the faster we can investigate.",
      },
      "Google Drive Resources": {
        title: "Tell us what’s happening with the resource",
        description:
          "Share the resource details and what you’ve already tried so we can better understand the issue.",
      },
    };

    return (
      copyByIssue[activeIssue.label] ?? {
        title: `Tell us more about ${activeIssue.label.toLowerCase()}`,
        description:
          "Share the details below so we can route your request to the right team and follow up with the right next steps.",
      }
    );
  }, [activeIssue]);

  function resetFlow(parent = selectedParent, issueLabel?: string) {
    setSelectedParent(parent);
    setSelectedIssueLabel(issueLabel ?? "");
    setFormValues({});
    setSubmittedPayload(null);
    setOpenResourceFieldId(null);
    setChatbotHandoff(null);
  }

  function handleParentSelect(parent: string) {
    setSelectedParent(parent);
    setSelectedIssueLabel("");
    setFormValues({});
    setSubmittedPayload(null);
    setResourceMenuOpen(false);
  }

  function handleIssueSelect(issueLabel: string) {
    setSelectedIssueLabel(issueLabel);
    setFormValues({});
    setSubmittedPayload(null);
    setOpenResourceFieldId(null);
  }

  function updateValue(fieldId: string, value: string) {
    setFormValues((current) => ({
      ...current,
      [fieldId]: value,
    }));
  }

  function handleAuthChange(nextAuthState: AuthState) {
    setAuthState(nextAuthState);
    setIsGuest(false);
    setFormValues({});
    setSubmittedPayload(null);
    setOpenResourceFieldId(null);
  }

  function handleChatEscalation(context: ChatHandoffContext) {
    setChatbotHandoff(context);
    setSubmittedPayload(null);

    if (authState === "logged_out") {
      setIsGuest(true);
    }

    window.setTimeout(() => {
      intakeSectionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 120);
  }

  function goBackToTopics() {
    setSelectedParent("");
    setSelectedIssueLabel("");
    setFormValues({});
    setOpenResourceFieldId(null);
  }

  function goBackToIssues() {
    setSelectedIssueLabel("");
    setFormValues({});
    setOpenResourceFieldId(null);
  }

  function isFieldMissing(field: FieldConfig) {
    if (!field.required) {
      return false;
    }

    return !String(formValues[field.id] ?? "").trim();
  }

  const formIsReady =
    Boolean(activeIssue) &&
    (authState === "logged_in" || isGuest) &&
    visibleFields.every((field) => !isFieldMissing(field));

  function handleSubmit() {
    if (!activeIssue || !formIsReady) {
      return;
    }

    const payload: SubmissionPayload = {
      authState,
      isGuest,
      parentTopic: selectedParent,
      issue: activeIssue.label,
      subject: activeIssue.subject,
      tags: activeIssue.tags,
      name:
        authState === "logged_in"
          ? loggedInIdentity?.name ?? null
          : authState === "logged_out" && isGuest
            ? formValues.guest_name ?? null
            : null,
      email:
        authState === "logged_in"
          ? loggedInIdentity?.email ?? null
          : authState === "logged_out" && isGuest
            ? formValues.guest_email ?? null
            : null,
      fields: visibleFields.reduce<FormValues>((accumulator, field) => {
        accumulator[field.id] = formValues[field.id] ?? "";
        return accumulator;
      }, {}),
      backendLogic: activeIssue.backendNote,
      chatbotHandoff,
    };

    console.log("TPT CX Genius Bar submission", payload);
    setSubmittedPayload(payload);
  }

  function renderField(field: FieldConfig) {
    const value = formValues[field.id] ?? "";
    const commonClassName =
      "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100";

    if (field.type === "textarea") {
      return (
        <textarea
          id={field.id}
          rows={4}
          className={commonClassName}
          placeholder={field.placeholder}
          value={value}
          onChange={(event) => updateValue(field.id, event.target.value)}
        />
      );
    }

    if (field.type === "select") {
      return (
        <div className="relative">
          <select
            id={field.id}
            className={clsx(commonClassName, "appearance-none pr-10")}
            value={value}
            onChange={(event) => updateValue(field.id, event.target.value)}
          >
            <option value="">Select an option</option>
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-4 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
        </div>
      );
    }

    if (field.type === "resource") {
      const selectedResource =
        MOCK_RESOURCES.find((resource) => resource.id === value) ?? null;
      const isOpen = openResourceFieldId === field.id;

      return (
        <div className="relative">
          <button
            type="button"
            className={clsx(
              commonClassName,
              "flex items-center justify-between text-left",
              !selectedResource && "text-slate-400",
            )}
            onClick={() =>
              setOpenResourceFieldId((current) =>
                current === field.id ? null : field.id,
              )
            }
          >
            <span className="flex min-w-0 items-center gap-3">
              <span
                className={clsx(
                  "flex h-10 w-14 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-[10px] font-semibold text-slate-700",
                  selectedResource?.accent ?? "from-slate-200 to-slate-50",
                )}
              >
                {selectedResource ? selectedResource.title.slice(0, 2) : "TPT"}
              </span>
              <span className="min-w-0">
                <span className="block truncate font-medium text-slate-900">
                  {selectedResource?.title ?? "Choose a purchased resource"}
                </span>
                <span className="block truncate text-xs text-slate-500">
                  {selectedResource?.seller ?? "Select from your purchased resources"}
                </span>
              </span>
            </span>
            <ChevronDown className="size-4 shrink-0 text-slate-400" />
          </button>

          {isOpen ? (
            <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-3xl border border-slate-200 bg-white p-2 shadow-[0_24px_60px_-24px_rgba(15,23,42,0.35)]">
              {MOCK_RESOURCES.map((resource) => (
                <button
                  key={`${field.id}-${resource.id}`}
                  type="button"
                  className="flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left transition hover:bg-emerald-50"
                  onClick={() => {
                    updateValue(field.id, resource.id);
                    setOpenResourceFieldId(null);
                  }}
                >
                  <span
                    className={clsx(
                      "flex h-14 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br text-xs font-semibold text-slate-700",
                      resource.accent,
                    )}
                  >
                    {resource.title.split(" ").slice(0, 2).join(" ")}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate font-medium text-slate-900">
                      {resource.title}
                    </span>
                    <span className="block truncate text-xs text-slate-500">
                      Seller: {resource.seller}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          ) : null}
        </div>
      );
    }

    return (
      <input
        id={field.id}
        type={field.type}
        className={commonClassName}
        placeholder={field.placeholder}
        value={value}
        onChange={(event) => updateValue(field.id, event.target.value)}
      />
    );
  }

  if (submittedPayload) {
    const submittedTagsPayload = {
      tags: submittedPayload.tags,
    };

    return (
      <div className="min-h-screen bg-[#fbfaf7] text-slate-900">
        <div className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-6 px-6 py-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#dff8ea] text-[#14473f]">
                <span className="text-2xl font-black">T</span>
              </div>
              <div className="text-4xl font-black tracking-tight text-[#14473f]">TPT</div>
            </div>
            <div className="hidden flex-1 items-center justify-center lg:flex">
              <div className="flex w-full max-w-3xl items-center rounded-full border border-slate-300 bg-white px-5 py-3 text-slate-400">
                <Search className="mr-3 size-5" />
                Search
                <div className="ml-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#63E0A5] text-[#14473f]">
                  <Search className="size-6" />
                </div>
              </div>
            </div>
            <div className="text-lg font-semibold text-slate-800">Log In | Sign Up</div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="rounded-3xl border border-emerald-100 bg-white p-8 shadow-[0_30px_90px_-60px_rgba(15,23,42,0.35)]">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-[#ab3f1f]">
                  Contact Us
                </p>
                <h1 className="mt-3 text-4xl font-semibold tracking-tight">
                  Thanks for reaching out.
                </h1>
                <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
                  Your request has been sent to TPT&apos;s Customer Experience team. Someone will get back to you as soon as possible.
                </p>
              </div>
              <button
                type="button"
                className="rounded-full border border-slate-200 px-5 py-3 text-sm font-medium text-slate-700 transition hover:border-emerald-300 hover:text-slate-900"
                onClick={() => {
                  setSubmittedPayload(null);
                  setFormValues({});
                  setChatbotHandoff(null);
                  setSelectedParent("");
                  setSelectedIssueLabel("");
                }}
              >
                Start another request
              </button>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
              <section className="rounded-[2rem] bg-[#14473f] p-7 text-white">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-emerald-100">
                  <CheckCircle2 className="size-6" />
                </div>
                <h2 className="mt-5 text-2xl font-semibold">Request summary</h2>
                <div className="mt-6 space-y-4 text-sm text-emerald-50/95">
                  <div className="flex items-center justify-between gap-4">
                    <span>Area</span>
                    <span className="font-medium text-white">{submittedPayload.parentTopic}</span>
                  </div>
                  <div className="flex items-center justify-between gap-4">
                    <span>Topic</span>
                    <span className="font-medium text-white">{submittedPayload.issue}</span>
                  </div>
                  <div className="flex items-center justify-between gap-4">
                    <span>Subject</span>
                    <span className="font-medium text-white">{submittedPayload.subject}</span>
                  </div>
                  <div className="flex items-center justify-between gap-4">
                    <span>Account state</span>
                    <span className="font-medium capitalize text-white">
                      {submittedPayload.authState.replace("_", " ")}
                    </span>
                  </div>
                </div>
              </section>

              <section className="rounded-[2rem] border border-slate-200 bg-[#fcfcfb] p-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-400">
                      Request details
                    </p>
                    <h2 className="mt-2 text-2xl font-semibold">Submission record</h2>
                  </div>
                  <button
                    type="button"
                    className="rounded-full bg-[#63E0A5] px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-[#50d792]"
                    onClick={() =>
                      navigator.clipboard?.writeText(
                        JSON.stringify(submittedTagsPayload, null, 2),
                      )
                    }
                  >
                    Copy details
                  </button>
                </div>
                <p className="mt-4 text-sm leading-7 text-slate-600">
                  Here are the tags that were attached to your request.
                </p>
                <pre className="mt-5 overflow-x-auto rounded-[1.5rem] bg-slate-950 p-5 text-xs leading-6 text-emerald-100">
                  {JSON.stringify(submittedTagsPayload, null, 2)}
                </pre>
              </section>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const trackerSteps = [
    { id: 1, label: "Area" },
    { id: 2, label: "Topic" },
    { id: 3, label: "Details" },
    { id: 4, label: "Sent" },
  ];

  return (
    <div className="min-h-screen bg-[#fbfaf7] text-slate-900">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-[1400px] px-6 py-6">
          <div className="flex items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#dff8ea] text-[#14473f]">
                <span className="text-2xl font-black">T</span>
              </div>
              <div className="text-4xl font-black tracking-tight text-[#14473f]">TPT</div>
            </div>
            <div className="hidden flex-1 items-center justify-center lg:flex">
              <div className="flex w-full max-w-4xl items-center rounded-full border border-slate-300 bg-white px-5 py-3 text-slate-400">
                <Search className="mr-3 size-5" />
                Search
                <div className="ml-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#63E0A5] text-[#14473f]">
                  <Search className="size-6" />
                </div>
              </div>
            </div>
            <div className="text-lg font-semibold text-slate-800">Log In | Sign Up</div>
          </div>
          <div className="mt-6 hidden items-center justify-between border-t border-slate-200 pt-5 text-[15px] font-medium text-slate-700 lg:flex">
            {[
              "Grade",
              "Resource type",
              "Seasonal",
              "ELA",
              "Math",
              "Science",
              "Social studies",
              "Languages",
              "Arts",
              "Special education",
              "Speech therapy",
            ].map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="rounded-[2rem] border border-slate-200 bg-white shadow-[0_25px_70px_-50px_rgba(15,23,42,0.3)]">
          <div className="border-b border-slate-200 px-6 py-8 sm:px-10">
            <p className="text-sm font-semibold text-[#ab3f1f]">
              Contact Us
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight">We&apos;re here to help!</h1>
            <p className="mt-4 max-w-4xl text-lg leading-8 text-slate-600">
              To get started, we&apos;ll walk you through a few quick steps. We&apos;ll only ask for the details we need so we can get your request to the right team as quickly as possible.
            </p>
          </div>

          <div className="border-b border-slate-200 bg-[#fcfcfb] px-6 py-6 sm:px-10">
            <div className="grid gap-4 md:grid-cols-4">
              {trackerSteps.map((step) => {
                const isComplete = step.id < currentStep;
                const isCurrent = step.id === currentStep;

                return (
                  <div key={step.id} className="flex items-center gap-3">
                    <div
                      className={clsx(
                        "flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold",
                        isCurrent
                          ? "bg-[#63E0A5] text-slate-950"
                          : isComplete
                            ? "bg-[#14473f] text-white"
                            : "bg-slate-100 text-slate-500",
                      )}
                    >
                      {step.id}
                    </div>
                    <p
                      className={clsx(
                        "text-base font-semibold",
                        isCurrent || isComplete ? "text-slate-900" : "text-slate-500",
                      )}
                    >
                      {step.label}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <section ref={intakeSectionRef} className="px-6 py-8 sm:px-10">
            <div className="mx-auto max-w-4xl">
              {currentStep === 1 ? (
                <>
                  <div className="max-w-3xl">
                    <h2 className="text-3xl font-semibold tracking-tight">
                      Which area best matches your problem?
                    </h2>
                    <p className="mt-3 text-lg leading-8 text-slate-600">
                      Choose the option that feels closest. If you&apos;re not sure, pick the best match and we&apos;ll guide you from there.
                    </p>
                  </div>

                  <div className="mt-8 grid gap-4 md:grid-cols-2">
                    {categoryEntries.map(([parent, category]) => (
                      <button
                        key={parent}
                        type="button"
                        className="rounded-[1.75rem] border border-slate-200 bg-white px-6 py-5 text-left transition hover:border-emerald-300 hover:bg-emerald-50/40"
                        onClick={() => handleParentSelect(parent)}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h3 className="text-xl font-semibold text-slate-900">{parent}</h3>
                            <p className="mt-3 text-sm leading-6 text-slate-500">
                              {category.description}
                            </p>
                          </div>
                          <ChevronRight className="mt-1 size-5 text-slate-400" />
                        </div>
                      </button>
                    ))}
                  </div>
                </>
              ) : null}

              {currentStep === 2 ? (
                <>
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      className="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-emerald-300 hover:text-slate-900"
                      onClick={goBackToTopics}
                    >
                      <ArrowLeft className="size-4" />
                      Back
                    </button>
                    <span className="rounded-full bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-800">
                      {selectedParent}
                    </span>
                  </div>

                  <div className="mt-6 max-w-3xl">
                    <h2 className="text-3xl font-semibold tracking-tight">
                      What would you like help with?
                    </h2>
                    <p className="mt-3 text-lg leading-8 text-slate-600">
                      Thanks for narrowing it down. Choose the topic that sounds closest and we&apos;ll ask for the right details next.
                    </p>
                  </div>

                  <div className="mt-8 grid gap-4 md:grid-cols-2">
                    {activeCategory?.issues.map((issue) => (
                      <button
                        key={issue.label}
                        type="button"
                        className="rounded-[1.75rem] border border-slate-200 bg-white px-6 py-5 text-left transition hover:border-emerald-300 hover:bg-emerald-50/40"
                        onClick={() => handleIssueSelect(issue.label)}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h3 className="text-xl font-semibold text-slate-900">{issue.label}</h3>
                            <p className="mt-3 text-sm leading-6 text-slate-500">
                              {issue.summary}
                            </p>
                          </div>
                          <ChevronRight className="mt-1 size-5 text-slate-400" />
                        </div>
                      </button>
                    ))}
                  </div>
                </>
              ) : null}

              {currentStep === 3 ? (
                <>
                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      className="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-emerald-300 hover:text-slate-900"
                      onClick={goBackToIssues}
                    >
                      <ArrowLeft className="size-4" />
                      Back
                    </button>
                    <span className="rounded-full bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-800">
                      {selectedParent}
                    </span>
                    <span className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600">
                      {activeIssue?.label}
                    </span>
                  </div>

                  <div className="mt-6 max-w-3xl">
                    <h2 className="text-3xl font-semibold tracking-tight">
                      {issueIntroCopy.title}
                    </h2>
                    <p className="mt-3 text-lg leading-8 text-slate-600">
                      {issueIntroCopy.description}
                    </p>
                  </div>

                  <div className="mt-8 space-y-6">
              {chatbotHandoff ? (
                <div className="rounded-[1.75rem] border border-emerald-200 bg-emerald-50 px-5 py-5 text-slate-800">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">
                        Chatbot handoff attached
                      </p>
                      <h3 className="mt-1 text-lg font-semibold">
                        We’ll carry the chatbot transcript into this request.
                      </h3>
                    </div>
                    <button
                      type="button"
                      className="rounded-full border border-emerald-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-emerald-300"
                      onClick={() => setChatbotHandoff(null)}
                    >
                      Clear handoff
                    </button>
                  </div>
                  <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                    <div className="rounded-2xl border border-emerald-100 bg-white px-4 py-3">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                        User type
                      </p>
                      <p className="mt-2 font-medium text-slate-900">
                        {chatbotHandoff.userType?.trim() || "Not specified"}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-emerald-100 bg-white px-4 py-3">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                        Original question
                      </p>
                      <p className="mt-2 font-medium text-slate-900">
                        {chatbotHandoff.originalQuestion}
                      </p>
                    </div>
                  </div>
                  {chatbotHandoff.restatedQuestion ? (
                    <div className="mt-3 rounded-2xl border border-emerald-100 bg-white px-4 py-3 text-sm">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                        Restated question
                      </p>
                      <p className="mt-2 font-medium text-slate-900">
                        {chatbotHandoff.restatedQuestion}
                      </p>
                    </div>
                  ) : null}
                  <div className="mt-3 rounded-2xl border border-emerald-100 bg-white px-4 py-3 text-sm">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                      Transcript preview
                    </p>
                    <div className="mt-2 space-y-2 text-slate-600">
                      {chatbotHandoff.transcript.slice(-4).map((message) => (
                        <p key={message.id}>
                          <span className="font-medium text-slate-900">
                            {message.role === "assistant" ? "Bot" : "User"}:
                          </span>{" "}
                          {message.content}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
              ) : null}

              {authState === "logged_in" ? (
                <div className="rounded-[1.75rem] border border-emerald-200 bg-emerald-50/60 px-5 py-4 text-sm text-slate-700">
                  We&apos;ll use the account you&apos;re signed in with:{" "}
                  <span className="font-medium text-slate-900">
                    {loggedInIdentity?.name}
                  </span>{" "}
                  ({loggedInIdentity?.email})
                </div>
              ) : null}

              {authState === "logged_out" && !isGuest ? (
                <div className="rounded-[1.75rem] border border-amber-200 bg-amber-50 px-5 py-5 text-slate-800">
                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-amber-600 shadow-sm">
                      <LogIn className="size-5" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold">Sign in or continue as a guest</h3>
                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        Signing in helps us fill in your account information automatically. If you&apos;d rather not, you can still continue as a guest.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-3">
                        <button
                          type="button"
                          className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
                          onClick={() => handleAuthChange("logged_in")}
                        >
                          Switch to Logged In
                        </button>
                        <button
                          type="button"
                          className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-emerald-300 hover:text-slate-900"
                          onClick={() => {
                            setIsGuest(true);
                            setFormValues({});
                          }}
                        >
                          Continue as Guest
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}
              <div className="rounded-[1.75rem] border border-slate-200 bg-white p-6">
                <div className="space-y-5">
                  {visibleFields.map((field) => (
                    <div key={field.id}>
                      <label
                        htmlFor={field.id}
                        className="mb-2 block text-sm font-medium text-slate-700"
                      >
                        {field.label}
                        {field.required ? (
                          <span className="ml-1 text-[#ab3f1f]">*</span>
                        ) : null}
                      </label>
                      {renderField(field)}
                      {field.helperText ? (
                        <p className="mt-2 text-xs leading-5 text-slate-500">
                          {field.helperText}
                        </p>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  className={clsx(
                    "inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-medium transition",
                    formIsReady
                      ? "bg-[#63E0A5] text-slate-950 hover:bg-[#4fd390]"
                      : "cursor-not-allowed bg-slate-200 text-slate-400",
                  )}
                  onClick={handleSubmit}
                  disabled={!formIsReady}
                >
                  Send message
                  <ChevronRight className="size-4" />
                </button>
              </div>
            </div>
                </>
              ) : null}
            </div>
          </section>
        </div>
      </div>
      <CxChatWidget onEscalate={handleChatEscalation} />
    </div>
  );
}

export default App;
