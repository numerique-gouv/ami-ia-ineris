################################################################################
############################### CUSTOM SECTION #################################
################################################################################

# Multi-stage build in order to minimize size
ARG CI_REGISTRY
# Build dependencies stage
FROM $CI_REGISTRY/heka/core/c13s:2 as compile-image
  # Install dependencies needed to build packages
  RUN apt-get update && apt-get install -y --no-install-recommends \
      g++ \
      python3-dev \
    && rm -rf /var/lib/apt/lists/*
  # Make sure scripts in .local are usable
  ENV PATH=/root/.local/bin:$PATH
  # Copy and install packages
  COPY requirements "$CUSTOM_ENDPOINTS_DIRECTORY/../requirements"
  RUN pip3 install --user -r $CUSTOM_ENDPOINTS_DIRECTORY/../requirements/requirements.txt

# Copy source-code stage
FROM $CI_REGISTRY/heka/core/c13s:2 as build-image

  COPY --from=compile-image /root/.local /root/.local
  # Make sure scripts in .local are usable
  ENV PATH=/root/.local/bin:$PATH
  # Install dependencies
  RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
    && rm -rf /var/lib/apt/lists/*
  # Copy custom endpoints (they are loaded from /sialab/launcher/endpoints/src)
  COPY src $CUSTOM_ENDPOINTS_DIRECTORY
