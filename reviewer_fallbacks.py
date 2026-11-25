"""Learner-requested use of original reviewer keys where no unique checked answer exists.

These are exam-preparation fallbacks, not independently confirmed technical answers.
The original review finding remains in reviewCaveat and checkedAnswerIndex stays None.
"""
FALLBACK_NOTES = {
    2: 'The reviewer marks the third choice. Two choices repeat the same service-isolation benefit, and the other choices also describe plausible MSA benefits. Use the marked choice for this reviewer; the NOT wording is ambiguous.',
    9: 'The reviewer marks Reverse engineering. Obfuscation makes reverse engineering harder; it does not perform reverse engineering. The choices omit a precise description of that purpose.',
    27: 'The reviewer marks the Compile statement. Its machine-language wording is too broad. The Deploy choice also confuses local and remote repositories, so the options contain more than one defect.',
    29: 'The reviewer calls this Bubble sort. The code compares each item with later items and swaps immediately. Conventional bubble sort compares adjacent items; the exact interchange-sort name is absent.',
    35: 'The reviewer marks the final UML annotation pair, printed as <>, <>. The source itself omits the stereotype names in that choice. Compare the original class diagram with the marked choice.',
    43: 'The reviewer marks (7,0), (5,0). That pair never makes x>0 false. The listed pairs do not establish full evaluated-condition coverage under short-circuit evaluation; retain this key for the supplied reviewer.',
    59: 'The reviewer marks the first numbered row. The supplied example shows bank standardization but omits the exact property that the question asks you to identify. The key supplies the intended selection.',
    60: 'The reviewer rejects the ACID statement. This reflects its simplified NoSQL classification. Some modern NoSQL products support ACID transactions, so this is a reviewer-specific answer.',
    64: 'The reviewer marks Diagram D. Its text allows a student without an association, while the diagram requires an association. Diagram C has a similar optionality conflict. All four original diagrams appear above.',
    66: 'The reviewer marks the first CAP statement. CAP describes a consistency/availability tradeoff during a network partition. The product classifications and several explanations are oversimplified.',
    71: 'The reviewer marks the extra-storage statement. Replication can increase storage, so that statement is a real tradeoff. The alternatives also mix user location transparency with database administration.',
    74: 'The reviewer marks the ordinary rows-and-columns description. That property is not distinctive of ORDB, but it remains true of an object-relational database. The question appears to intend a distinguishing feature.',
    76: 'The reviewer selects attributes and identifiers. Modeling methods divide conceptual and logical tasks differently. Subject areas and conceptual ERDs can also belong to conceptual modeling.',
    80: 'The reviewer rejects the filesystem-storage statement. That fits an internal-LOB interpretation. External LOBs, such as Oracle BFILE, can use operating-system files; the question does not state the storage type.',
    87: 'The reviewer rejects departments without employees. The source mixes optionality and mandatory wording in its Barker relationship example. Use its marked interpretation for this item.',
    101: 'The reviewer selects personalized ASP/JSP order pages. Such responses normally should not use a shared public cache. A CDN can still proxy dynamic content, so the absolute wording is too broad.',
    116: 'The reviewer marks the NameNode/DataNode statement. That statement describes the actual HDFS division of responsibilities. The other choices use broad wording, so retain this answer as the reviewer key rather than a confirmed false claim.',
    127: 'The reviewer marks the root-only write restriction on /etc/profile. That restriction is valid hardening. Another choice incorrectly describes hosts.allow and hosts.deny entries as users; the source key is disputed.',
    131: 'The reviewer selects chown, which changes file ownership. The referenced improvement plan is missing from the source example. Its absent requirements prevent an independent choice of command.',
    136: 'The reviewer marks the Log4j update statement. Updating to a supported fixed release is a valid mitigation. Use the source key for this reviewer without learning that updates are an incorrect security action.',
    138: 'The reviewer selects RBAC. Its matrix lists users and permissions but does not show roles or memberships. A permission matrix alone does not uniquely identify the access-control model.',
    145: 'The reviewer selects OAuth for social login. OAuth handles delegated authorization; OpenID Connect adds authentication. OAuth is the intended choice among the supplied options, which omit OpenID Connect.',
    152: 'The reviewer rejects allowing operation on rooted or jailbroken devices. This follows its conservative mobile-security policy. Actual blocking policy depends on the application and its risk assessment.',
    180: 'The reviewer rejects the single-repository description of a data lake. That description is plausible. Other options describe task-specific or transformed data, so the NOT question does not isolate one technical answer.',
    184: 'The reviewer marks the duty to report every breach. Treat this as the supplied historical key. The applicable notification rules depend on the jurisdiction and effective date, which the question does not establish.',
    202: 'The reviewer selects (d)-(a)-(c)-(b). The example does not define its ISP phase model, and its ordering places scheduling and design in a disputed sequence. Use the printed key for this reviewer.',
    208: 'The reviewer selects the BMT statement. Other choices also misplace content between the RFP sections. The printed key identifies the intended selection despite those category inconsistencies.',
    223: 'The reviewer selects Bar Chart. The prompt mixes distribution, correlation, and outlier descriptions. No listed chart cleanly satisfies every feature, so this is the reviewer answer rather than a checked chart recommendation.',
    225: 'The reviewer rejects the monthly-sales bands. The purchase-date bands also overlap, and other groups have unclear boundaries. Retain the marked choice for this ambiguous MECE item.',
    234: 'The reviewer rejects the Expected value statement. An expected value normally describes the anticipated result, so that wording is not inherently false. Use the printed key for this reviewer.',
}

CHOICE_REPAIRS = {
    35: ['{End Of Service}', 'Engine#1, Engine#2', '{level = 1.0}, {level = 1.2}', 'UML annotation pair: <>, <> (as printed in the reviewer)'],
    64: ['Diagram A — Department and Student', 'Diagram B — Student and Locker', 'Diagram C — Advisor and Student', 'Diagram D — Student Association and Student'],
}

# These four findings originally came from the import audit.
BASE_CAVEATS = {2: 'Two choices repeat the same service-isolation benefit, and the other choices also describe plausible benefits of microservices. This NOT question has no defensible single answer.', 35: 'The last answer choice lost the UML stereotype text during PDF extraction and appears only as two empty angle-bracket pairs. It cannot be scored accurately from the available choices.', 180: 'A data lake holds varied source data for broad future use. The marked single repository description is plausible, while more than one other choice describes task-specific or already transformed data. This NOT item needs a clearer key.', 223: 'The description mixes distribution, correlation, and outlier language. The available choices do not contain a clear single chart that satisfies every part; the red Bar Chart mark is unsupported. Study only.'}
