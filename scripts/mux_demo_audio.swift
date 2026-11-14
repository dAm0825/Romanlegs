import AVFoundation
import Foundation

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let videoURL = root.appendingPathComponent("work/offerguard-demo-video.mp4")
let audioURL = root.appendingPathComponent("work/demo-narration.aiff")
let outputURL = root.appendingPathComponent("work/OfferGuard-competition-demo.mp4")

if FileManager.default.fileExists(atPath: outputURL.path) {
    try FileManager.default.removeItem(at: outputURL)
}

let videoAsset = AVURLAsset(url: videoURL)
let audioAsset = AVURLAsset(url: audioURL)
let composition = AVMutableComposition()

guard
    let sourceVideo = videoAsset.tracks(withMediaType: .video).first,
    let videoTrack = composition.addMutableTrack(
        withMediaType: .video,
        preferredTrackID: kCMPersistentTrackID_Invalid
    )
else {
    fatalError("Video track is unavailable")
}

let videoRange = CMTimeRange(start: .zero, duration: videoAsset.duration)
try videoTrack.insertTimeRange(videoRange, of: sourceVideo, at: .zero)
videoTrack.preferredTransform = sourceVideo.preferredTransform

if
    let sourceAudio = audioAsset.tracks(withMediaType: .audio).first,
    let audioTrack = composition.addMutableTrack(
        withMediaType: .audio,
        preferredTrackID: kCMPersistentTrackID_Invalid
    )
{
    try audioTrack.insertTimeRange(
        CMTimeRange(start: .zero, duration: audioAsset.duration),
        of: sourceAudio,
        at: .zero
    )
}

guard let exporter = AVAssetExportSession(
    asset: composition,
    presetName: AVAssetExportPreset1920x1080
) else {
    fatalError("Unable to create export session")
}
exporter.outputURL = outputURL
exporter.outputFileType = .mp4
exporter.shouldOptimizeForNetworkUse = true

let semaphore = DispatchSemaphore(value: 0)
exporter.exportAsynchronously {
    semaphore.signal()
}
semaphore.wait()

guard exporter.status == .completed else {
    fatalError("Audio mux failed: \(String(describing: exporter.error))")
}
print("Exported: \(outputURL.path)")
