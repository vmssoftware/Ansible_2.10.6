OS := $(shell uname -s)
SITELIB = $(shell python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"):
PLUGIN_FORMATTER=../../hacking/build-ansible.py docs-build
TESTING_FORMATTER=../bin/testing_formatter.sh
KEYWORD_DUMPER=../../hacking/build-ansible.py document-keywords
CONFIG_DUMPER=../../hacking/build-ansible.py document-config
GENERATE_CLI=../../hacking/build-ansible.py generate-man
COLLECTION_DUMPER=../../hacking/build-ansible.py collection-meta
ifeq ($(shell echo $(OS) | egrep -ic 'Darwin|FreeBSD|OpenBSD|DragonFly'),1)
CPUS ?= $(shell sysctl hw.ncpu|awk '{print $$2}')
else
CPUS ?= $(shell nproc)
endif

# Sets the build output directory for the main docsite if it's not already specified
ifndef BUILDDIR
	BUILDDIR = _build
endif

# Backwards compat for separate VARS
PLUGIN_ARGS=
ifdef MODULES
ifndef PLUGINS
	PLUGIN_ARGS = -l $(MODULES)
else
	PLUGIN_ARGS = -l $(MODULES),$(PLUGINS)
endif
else
ifdef PLUGINS
	PLUGIN_ARGS = -l $(PLUGINS)
endif
endif


DOC_PLUGINS ?= become cache callback cliconf connection httpapi inventory lookup netconf shell strategy vars

PYTHON=python
# fetch version from project release.py as single source-of-truth
VERSION := $(shell $(PYTHON) ../../packaging/release/versionhelper/version_helper.py --raw || echo error)
ifeq ($(findstring error,$(VERSION)), error)
$(error "version_helper failed")
endif

assertrst:
ifndef rst
	$(error specify document or pattern with rst=somefile.rst)
endif

all: docs

docs: htmldocs

generate_rst: collections_meta config cli keywords plugins testing
base_generate_rst: collections_meta config cli keywords base_plugins testing

htmldocs: generate_rst
	CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx html

base_htmldocs: base_generate_rst
	CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx html

singlehtmldocs: generate_rst
	CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx singlehtml

base_singlehtmldocs: base_generate_rst
	CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx singlehtml

linkcheckdocs: generate_rst
		CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx linkcheck

webdocs: docs

#TODO: leaving htmlout removal for those having older versions, should eventually be removed also
clean:
	@echo "Cleaning $(BUILDDIR)"
	-rm -rf $(BUILDDIR)/doctrees
	-rm -rf $(BUILDDIR)/html
	-rm -rf htmlout
	-rm -rf module_docs
	-rm -rf $(BUILDDIR)
	-rm -f .buildinfo
	-rm -f objects.inv
	-rm -rf *.doctrees
	@echo "Cleaning up minified css files"
	find . -type f -name "*.min.css" -delete
	@echo "Cleaning up byte compiled python stuff"
	find . -regex ".*\.py[co]$$" -delete
	@echo "Cleaning up editor backup files"
	find . -type f \( -name "*~" -or -name "#*" \) -delete
	find . -type f \( -name "*.swp" \) -delete
	@echo "Cleaning up generated rst"
	rm -f rst/playbooks_directives.rst
	rm -f rst/reference_appendices/config.rst
	rm -f rst/reference_appendices/playbooks_keywords.rst
	rm -f rst/dev_guide/collections_galaxy_meta.rst
	rm -f rst/cli/*.rst
	for filename in `ls rst/collections/` ; do \
		if test x"$$filename" != x'all_plugins.rst' ; then \
			rm -rf "rst/collections/$$filename"; \
		fi \
	done
	@echo "Cleaning up legacy generated rst locations"
	rm -rf rst/modules
	rm -f rst/plugins/*/*.rst

.PHONY: docs clean

collections_meta: ../templates/collections_galaxy_meta.rst.j2
	$(COLLECTION_DUMPER) --template-file=../templates/collections_galaxy_meta.rst.j2 --output-dir=rst/dev_guide/ ../../lib/ansible/galaxy/data/collections_galaxy_meta.yml

# TODO: make generate_man output dir cli option
cli:
	mkdir -p rst/cli
	$(GENERATE_CLI) --template-file=../templates/cli_rst.j2 --output-dir=rst/cli/ --output-format rst ../../lib/ansible/cli/*.py

keywords: ../templates/playbooks_keywords.rst.j2
	$(KEYWORD_DUMPER) --template-dir=../templates --output-dir=rst/reference_appendices/ ./keyword_desc.yml

config: ../templates/config.rst.j2
	$(CONFIG_DUMPER) --template-file=../templates/config.rst.j2 --output-dir=rst/reference_appendices/ ../../lib/ansible/config/base.yml

# For now, if we're building on devel, just build base docs.  In the future we'll want to build docs that
# are the latest versions on galaxy (using a different antsibull-docs subcommand)
plugins:
	if expr "$(VERSION)" : '.*[.]dev[0-9]\{1,\}$$' &> /dev/null; then \
		$(PLUGIN_FORMATTER) base -o rst $(PLUGIN_ARGS);\
	else \
		$(PLUGIN_FORMATTER) full -o rst $(PLUGIN_ARGS);\
	fi

# This only builds the plugin docs included with ansible-base
base_plugins:
	$(PLUGIN_FORMATTER) base -o rst $(PLUGIN_ARGS);\

testing:
	$(TESTING_FORMATTER)

epub:
	(CPUS=$(CPUS) $(MAKE) -f Makefile.sphinx epub)

htmlsingle: assertrst
	sphinx-build -j $(CPUS) -b html -d $(BUILDDIR)/doctrees ./rst $(BUILDDIR)/html rst/$(rst)
	@echo "Output is in $(BUILDDIR)/html/$(rst:.rst=.html)"
