import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SubmissionDescriptionMetsGenerator:
    """Compatibility generator for submission-description METS templates."""

    NAMESPACES = {
        "mets": "http://www.loc.gov/METS/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    DEFAULT_DUBLIN_CORE_FIELDS: List[str] = [
        "title",
        "creator",
        "subject",
        "description",
        "publisher",
        "contributor",
        "date",
        "type",
        "format",
        "identifier",
        "source",
        "language",
        "relation",
        "coverage",
        "rights",
    ]

    def __init__(self) -> None:
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)

    def create_submission_mets_xml(self, metadata: Dict[str, Any]) -> ET.Element:
        """Create a submission description METS XML element tree root."""
        mets_ns = self.NAMESPACES["mets"]
        dc_ns = self.NAMESPACES["dc"]
        xsi_ns = self.NAMESPACES["xsi"]

        package_type = (metadata.get("package_type") or metadata.get("type") or "SIP").strip().upper()
        objid = metadata.get("objid") or f"SUBMISSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        root = ET.Element(f"{{{mets_ns}}}mets")
        root.set("OBJID", objid)
        root.set("TYPE", package_type)
        root.set("PROFILE", metadata.get("profile", "DIAS_SUBMISSION_DESCRIPTION"))
        root.set("LABEL", metadata.get("label", ""))
        root.set(
            f"{{{xsi_ns}}}schemaLocation",
            f"{mets_ns} submissionDescription.xsd",
        )

        mets_hdr = ET.SubElement(root, f"{{{mets_ns}}}metsHdr")
        mets_hdr.set("CREATEDATE", datetime.now().astimezone().isoformat())
        mets_hdr.set("RECORDSTATUS", metadata.get("record_status", "NEW"))

        for agent_data in metadata.get("agents", []):
            agent = ET.SubElement(mets_hdr, f"{{{mets_ns}}}agent")
            agent.set("ROLE", agent_data.get("role", "OTHER"))
            agent.set("TYPE", agent_data.get("type", "ORGANIZATION"))
            other_role = agent_data.get("otherrole")
            if other_role:
                agent.set("OTHERROLE", other_role)
            other_type = agent_data.get("othertype")
            if other_type:
                agent.set("OTHERTYPE", other_type)

            name_elem = ET.SubElement(agent, f"{{{mets_ns}}}name")
            name_elem.text = str(agent_data.get("name", "Unknown"))

            note = agent_data.get("note")
            if note:
                note_elem = ET.SubElement(agent, f"{{{mets_ns}}}note")
                note_elem.text = str(note)

        for alt_record in metadata.get("alt_record_ids", []):
            alt = ET.SubElement(mets_hdr, f"{{{mets_ns}}}altRecordID")
            alt.set("TYPE", str(alt_record.get("type", "")))
            alt.text = str(alt_record.get("value", ""))

        mets_doc = ET.SubElement(mets_hdr, f"{{{mets_ns}}}metsDocumentID")
        mets_doc.set("TYPE", metadata.get("mets_document_id_type", "UUID"))
        mets_doc.text = metadata.get("mets_document_id") or str(uuid.uuid4())

        dmd_sec = ET.SubElement(root, f"{{{mets_ns}}}dmdSec")
        md_wrap = ET.SubElement(dmd_sec, f"{{{mets_ns}}}mdWrap")
        md_wrap.set("MDTYPE", "DC")
        xml_data = ET.SubElement(md_wrap, f"{{{mets_ns}}}xmlData")

        descriptive_metadata = metadata.get("descriptive_metadata", {})
        for field in self.DEFAULT_DUBLIN_CORE_FIELDS:
            value = descriptive_metadata.get(field, "")
            elem = ET.SubElement(xml_data, f"{{{dc_ns}}}{field}")
            elem.text = "" if value is None else str(value)

        return root

    def save_mets_xml(self, mets_xml: ET.Element, output_path: str | Path) -> None:
        """Save METS XML to file path with pretty indentation."""
        output = Path(output_path)
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            tree = ET.ElementTree(mets_xml)
            ET.indent(tree, space="    ", level=0)
            tree.write(output, encoding="UTF-8", xml_declaration=True)
        except Exception as exc:
            logger.error(f"Failed to save metadata XML to {output}: {exc}")
            raise
