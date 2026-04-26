import { Box, Skeleton, alpha, styled } from '@mui/material';
import { useState } from 'react';

type ResponsiveImageProps = {
  src?: string;
  alt: string;
  aspectRatio?: string | number;
  borderRadius?: number | string;
  objectFit?: 'cover' | 'contain' | 'fill';
  maxWidth?: string | number;
  height?: string | number;
  className?: string;
};

const ImageWrapper = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'aspectRatio' && prop !== 'borderRadius' && prop !== 'maxWidth',
})<{ aspectRatio?: string | number; borderRadius?: number | string; maxWidth?: string | number }>(
  ({ aspectRatio, borderRadius, maxWidth }) => ({
    position: 'relative',
    width: '100%',
    maxWidth: maxWidth || '100%',
    aspectRatio: aspectRatio || 'auto',
    borderRadius: borderRadius || 0,
    overflow: 'hidden',
    backgroundColor: alpha('#000', 0.02),
  })
);

const StyledImage = styled('img', {
  shouldForwardProp: (prop) => prop !== 'objectFit' && prop !== 'loaded',
})<{ objectFit: string; loaded: boolean }>(({ objectFit, loaded }) => ({
  display: 'block',
  width: '100%',
  height: '100%',
  objectFit: objectFit as any,
  opacity: loaded ? 1 : 0,
  transition: 'opacity 0.4s ease-in-out',
}));

export function ResponsiveImage({
  src,
  alt,
  aspectRatio = '16 / 9',
  borderRadius = 16,
  objectFit = 'cover',
  maxWidth,
  height,
  className,
}: ResponsiveImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  if (!src || error) {
    return (
      <ImageWrapper 
        aspectRatio={aspectRatio} 
        borderRadius={borderRadius} 
        maxWidth={maxWidth}
        sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: alpha('#000', 0.05) }}
      >
        <Box sx={{ color: 'text.disabled', fontSize: '0.75rem', fontWeight: 600 }}>
          {error ? 'Image Error' : 'No Image'}
        </Box>
      </ImageWrapper>
    );
  }

  return (
    <ImageWrapper 
      aspectRatio={aspectRatio} 
      borderRadius={borderRadius} 
      maxWidth={maxWidth}
      className={className}
    >
      {!loaded && (
        <Skeleton 
          variant="rectangular" 
          width="100%" 
          height="100%" 
          animation="wave"
          sx={{ position: 'absolute', top: 0, left: 0, zIndex: 1 }}
        />
      )}
      <StyledImage
        src={src}
        alt={alt}
        objectFit={objectFit}
        loaded={loaded}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        style={{ height: height || '100%' }}
      />
    </ImageWrapper>
  );
}
