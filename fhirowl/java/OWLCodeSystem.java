package org.hl7.fhir.definitions.generators.specification;

import org.apache.jena.ontology.OntClass;
import org.apache.jena.ontology.OntModel;
import org.apache.jena.ontology.OntModelSpec;
import org.apache.jena.ontology.Ontology;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFFormat;
import org.apache.jena.vocabulary.OWL2;
import org.apache.jena.vocabulary.RDF;
import org.apache.jena.vocabulary.RDFS;
import org.apache.jena.vocabulary.SKOS;
import org.hl7.fhir.r4.model.CodeSystem;
import org.hl7.fhir.rdf.RDFNamespace;
import org.hl7.fhir.utilities.Utilities;

import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * Created by mrf7578 on 6/28/17.
 */
public class OWLCodeSystem {
    OntModel model;
    RDFNamespace CSNS;

    public OWLCodeSystem(CodeSystem cs) throws Exception {
        model = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);
        model.setNsPrefix(RDFNamespace.W5.getPrefix(), RDFNamespace.W5.getURI());
        model.setNsPrefix(RDFNamespace.FHIR.getPrefix(), RDFNamespace.FHIR.getURI());
        model.setNsPrefix("skos", SKOS.getURI());

        CSNS = new RDFNamespace(cs.getId(), cs.getUrl() + '/');
        model.setNsPrefix(CSNS.getPrefix(), CSNS.getURI());

        Ontology ontology = model.createOntology(CSNS.getURI());
        String title = cs.getTitle() != null? cs.getTitle() : cs.getName();
        ontology.addLabel(title, null);
        if (cs.getDescription() != null)
            ontology.addComment(cs.getDescription(), null);
        ontology.setVersionInfo(title + '(' + cs.getVersion() + ')');
        ontology.addProperty(OWL2.versionIRI, CSNS.getURI() + cs.getVersion());

        for(CodeSystem.ConceptDefinitionComponent c : cs.getConcept())
            addConcept(c);
    }

    public void commit(CodeSystem cs, String destDir) throws Exception {
        FileOutputStream destination = new FileOutputStream(Utilities.path(fullDestDir(destDir, cs.getUrl()), fullFileName(cs.getId(), cs.getUrl())));
        RDFDataMgr.write(destination, model, RDFFormat.TURTLE_PRETTY);
        destination.flush();
        destination.close();
    }

    private String fullDestDir(String destDir, String csUrl) {
        if (csUrl.contains("/v2/")) {
            return destDir + "/" + csUrl.substring(csUrl.indexOf("/v2/"));
        } else if (csUrl.contains("/v3/")) {
            return destDir + "/" + csUrl.substring(csUrl.indexOf("/v3/"));
        } else
            return destDir;
    }

    private String fullFileName(String baseName, String csUrl) {
        if (csUrl.contains("/v2/"))
            return baseName + ".cs.owl";
        else if (csUrl.contains("/v3"))
            return baseName + ".cs.owl";
        else
            return "codesystem-" + baseName + ".owl";
    }

    private OntClass addConcept(CodeSystem.ConceptDefinitionComponent concept) {
        OntClass c = model.createClass(CSNS.uriFor(concept.getCode()));
        String label = concept.getDisplay() != null? concept.getDisplay() : concept.getCode();
        c.addLabel(label, null);
        c.addProperty(SKOS.prefLabel, label);
        if (concept.getDefinition() != null)
            c.addProperty(SKOS.definition, concept.getDefinition());
        for(CodeSystem.ConceptDefinitionComponent subClass : concept.getConcept()) {
            c.addSubClass(addConcept(subClass));
        }
        return c;
    }

}
